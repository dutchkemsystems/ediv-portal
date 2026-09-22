import csv
import io
import json
import os
import subprocess
import tempfile
from datetime import datetime

from django.db import models
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from config.permissions import IsAdminOrTGOrDeptHead
from config.security import AuditLogger

from .access_mapping import ACCESS_TABLE_MAPPINGS, find_mapping_for_table
from .models import AccessDatabase, AccessPrivilege, AccessTableData
from .models import ImportError as ImportErrorModel
from .models import ImportJob
from .serializers import (
    AccessDatabaseListSerializer,
    AccessDatabaseSerializer,
    AccessPrivilegeSerializer,
    AccessTableDataSerializer,
    ImportJobListSerializer,
    ImportJobSerializer,
)

EXPORTABLE_MODELS = {
    "students": {
        "model_path": "apps.students.models",
        "model_name": "Student",
        "fields": ["id", "first_name", "last_name", "email", "student_id", "date_of_birth", "gender"],
    },
    "staff": {
        "model_path": "apps.staff.models",
        "model_name": "Staff",
        "fields": ["id", "first_name", "last_name", "email", "employee_id", "department", "position"],
    },
    "schools": {
        "model_path": "apps.schools.models",
        "model_name": "School",
        "fields": ["id", "name", "code", "address", "phone", "email", "principal_name"],
    },
}

ACCESS_SYNC_MODELS = {
    "students": {"model_path": "apps.students.models", "model_name": "Student"},
    "staff": {"model_path": "apps.staff.models", "model_name": "Staff"},
    "schools": {"model_path": "apps.schools.models", "model_name": "School"},
}


class TableDataPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 500


def _import_rows(rows, target_model, job):
    imported = 0
    errors = []
    model_config = EXPORTABLE_MODELS.get(target_model)
    if not model_config:
        return 0, [{"row": 0, "field": "", "error": f"Unknown model: {target_model}", "raw": ""}]

    try:
        parts = model_config["model_path"].split(".")
        module = __import__(parts[0], fromlist=[parts[1]])
        for part in parts[1:]:
            module = getattr(module, part)
        model_cls = getattr(module, model_config["model_name"])
    except (ImportError, AttributeError) as e:
        return 0, [{"row": 0, "field": "", "error": f"Model load failed: {e}", "raw": ""}]

    valid_fields = set(f.name for f in model_cls._meta.get_fields() if hasattr(f, "column"))

    for i, row in enumerate(rows, start=1):
        try:
            filtered = {k: v for k, v in row.items() if k in valid_fields and v}
            if not filtered:
                errors.append({"row": i, "field": "", "error": "No valid fields", "raw": json.dumps(row)})
                continue
            model_cls.objects.create(**filtered)
            imported += 1
        except Exception as e:
            errors.append({"row": i, "field": "", "error": str(e), "raw": json.dumps(row)})

    return imported, errors


def _detect_access_driver():
    try:
        import pyodbc

        drivers = [d for d in pyodbc.drivers() if "Access" in d]
        if drivers:
            return "pyodbc"
    except ImportError:
        pass
    try:
        result = subprocess.run(["mdb-tables", "--version"], capture_output=True, timeout=5)
        if result.returncode == 0:
            return "mdbtools"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def _parse_access_tables(tmp_path, driver):
    tables = {}
    if driver == "mdbtools":
        try:
            result = subprocess.run(["mdb-tables", "-1", tmp_path], capture_output=True, text=True, timeout=30)
            table_names = [t.strip() for t in result.stdout.strip().split("\n") if t.strip()]
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return {}
        for tbl in table_names:
            try:
                result = subprocess.run(
                    ["mdb-export", "-1", tmp_path, tbl],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    encoding="utf-8-sig",
                )
                reader = csv.DictReader(io.StringIO(result.stdout))
                rows = list(reader)
                if rows:
                    tables[tbl] = rows
            except Exception:
                continue
    elif driver == "pyodbc":
        try:
            import pyodbc

            conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={tmp_path};"
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            table_list = [row.table_name for row in cursor.tables(tableType="TABLE")]
            for tbl in table_list:
                try:
                    cursor.execute(f"SELECT * FROM [{tbl}]")
                    columns = [desc[0] for desc in cursor.description]
                    rows = []
                    for row in cursor.fetchall():
                        rows.append(
                            {columns[i]: str(row[i]) if row[i] is not None else "" for i in range(len(columns))}
                        )
                    if rows:
                        tables[tbl] = rows
                except Exception:
                    continue
            conn.close()
        except Exception:
            pass
    return tables


def _has_write_permission(user, database):
    if user.role in ("SYSADMIN", "TG_PS"):
        return True
    privilege = AccessPrivilege.objects.filter(database=database, user=user).first()
    return privilege and privilege.privilege_level in ("EDIT", "DELETE", "ADMIN")


def _has_admin_permission(user, database):
    if user.role in ("SYSADMIN", "TG_PS"):
        return True
    privilege = AccessPrivilege.objects.filter(database=database, user=user).first()
    return privilege and privilege.privilege_level == "ADMIN"


class ImportJobViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrTGOrDeptHead]

    def get_serializer_class(self):
        if self.action == "list":
            return ImportJobListSerializer
        return ImportJobSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ("SYSADMIN", "TG_PS"):
            return ImportJob.objects.all()
        return ImportJob.objects.filter(created_by=user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def _parse_access_file(self, uploaded_file, ext, target_model):
        mapping = ACCESS_TABLE_MAPPINGS.get(target_model)
        table_aliases = mapping.get("table_aliases", []) if mapping else []

        with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        try:
            driver = _detect_access_driver()
            if not driver:
                return [{"error": "No Access driver available. Convert to CSV first."}]

            if driver == "mdbtools":
                return self._parse_with_mdbtools(tmp_path, table_aliases, mapping)
            elif driver == "pyodbc":
                return self._parse_with_pyodbc(tmp_path, table_aliases, mapping)
        finally:
            os.unlink(tmp_path)

    def _parse_with_mdbtools(self, db_path, table_aliases, mapping):
        try:
            result = subprocess.run(["mdb-tables", "-1", db_path], capture_output=True, text=True, timeout=30)
            all_tables = [t.strip() for t in result.stdout.strip().split("\n") if t.strip()]
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return []

        target_table = None
        for alias in table_aliases:
            for t in all_tables:
                if t.lower().replace(" ", "_").replace("-", "_") == alias.lower().replace(" ", "_").replace("-", "_"):
                    target_table = t
                    break
            if target_table:
                break

        if not target_table and all_tables:
            target_table = all_tables[0]

        if not target_table:
            return []

        try:
            result = subprocess.run(
                ["mdb-export", db_path, target_table],
                capture_output=True,
                text=True,
                timeout=60,
                encoding="utf-8-sig",
            )
            reader = csv.DictReader(io.StringIO(result.stdout))
            rows = list(reader)
            if mapping:
                rows = self._apply_access_mapping(rows, mapping)
            return rows
        except Exception:
            return []

    def _parse_with_pyodbc(self, db_path, table_aliases, mapping):
        try:
            import pyodbc

            conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path};"
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()

            tables = [row.table_name for row in cursor.tables(tableType="TABLE")]
            target_table = None
            for alias in table_aliases:
                for t in tables:
                    if t.lower().replace(" ", "_") == alias.lower().replace(" ", "_"):
                        target_table = t
                        break
                if target_table:
                    break
            if not target_table and tables:
                target_table = tables[0]

            if not target_table:
                conn.close()
                return []

            cursor.execute(f"SELECT * FROM [{target_table}]")
            columns = [desc[0] for desc in cursor.description]
            rows = []
            for row in cursor.fetchall():
                rows.append({columns[i]: str(row[i]) if row[i] is not None else "" for i in range(len(columns))})
            conn.close()

            if mapping:
                rows = self._apply_access_mapping(rows, mapping)
            return rows
        except Exception:
            return []

    def _apply_access_mapping(self, rows, mapping):
        field_map = mapping.get("field_map", {})
        transforms = mapping.get("transforms", {})
        name_fields = mapping.get("name_fields", {})
        mapped_rows = []

        for row in rows:
            new_row = {}
            for access_col, value in row.items():
                access_key = access_col.lower().replace(" ", "_").replace("-", "_")
                django_field = field_map.get(access_key)
                if not django_field:
                    for fk, fk_aliases in field_map.items():
                        if access_key == fk.lower():
                            django_field = fk
                            break

                if not django_field or django_field.startswith("_skip"):
                    if django_field and django_field.startswith("_skip"):
                        target_name = django_field.replace("_skip_", "")
                        if target_name in name_fields:
                            parts = str(value).strip().split(" ", 1) if value else ["", ""]
                            new_row[target_name] = parts[0]
                            if len(name_fields[target_name]) > 1:
                                new_row[name_fields[target_name][1]] = parts[1] if len(parts) > 1 else ""
                    continue

                if django_field in transforms:
                    try:
                        value = transforms[django_field](value)
                    except Exception:
                        pass

                if value is not None:
                    new_row[django_field] = str(value).strip() if isinstance(value, str) else value

            for field_name, aliases in name_fields.items():
                if field_name not in new_row:
                    for alias in aliases:
                        if alias in row and row[alias]:
                            parts = str(row[alias]).strip().split(" ", 1)
                            new_row[field_name] = parts[0]
                            if len(aliases) > 1 and len(parts) > 1:
                                new_row[aliases[1]] = parts[1]
                            break

            mapped_rows.append(new_row)
        return mapped_rows

    @action(detail=False, methods=["post"], url_path="import")
    def import_data(self, request):
        uploaded_file = request.FILES.get("file")
        target_model = request.data.get("model", "")

        if not uploaded_file:
            return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)
        if target_model not in EXPORTABLE_MODELS:
            return Response(
                {"error": f"Invalid model. Choose from: {list(EXPORTABLE_MODELS.keys())}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        file_name = uploaded_file.name
        ext = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""

        type_map = {
            "csv": "CSV",
            "xlsx": "EXCEL",
            "xls": "EXCEL",
            "pdf": "PDF",
            "docx": "WORD",
            "json": "JSON",
            "accdb": "ACCESS",
            "mdb": "ACCESS",
        }
        file_type = type_map.get(ext, "CSV")

        job = ImportJob.objects.create(
            file_name=file_name,
            file_type=file_type,
            target_model=target_model,
            status="PROCESSING",
            created_by=request.user,
        )

        rows = []
        try:
            if ext == "csv":
                content = uploaded_file.read().decode("utf-8-sig")
                reader = csv.DictReader(io.StringIO(content))
                rows = list(reader)
            elif ext in ("xlsx", "xls"):
                import openpyxl

                wb = openpyxl.load_workbook(uploaded_file, read_only=True)
                ws = wb.active
                headers = [str(cell.value).strip() if cell.value else "" for cell in next(ws.iter_rows(max_row=1))]
                for row in ws.iter_rows(min_row=2, values_only=True):
                    rows.append(
                        {headers[i]: str(v) if v is not None else "" for i, v in enumerate(row) if i < len(headers)}
                    )
                wb.close()
            elif ext == "json":
                content = uploaded_file.read().decode("utf-8")
                data = json.loads(content)
                if isinstance(data, list):
                    rows = data
                elif isinstance(data, dict) and "data" in data:
                    rows = data["data"]
                else:
                    rows = [data]
            elif ext == "pdf":
                import pdfplumber

                with pdfplumber.open(uploaded_file) as pdf:
                    for page in pdf.pages:
                        table = page.extract_table()
                        if table and len(table) > 1:
                            headers = [str(h).strip() if h else "" for h in table[0]]
                            for row in table[1:]:
                                rows.append(
                                    {headers[i]: str(v) if v else "" for i, v in enumerate(row) if i < len(headers)}
                                )
            elif ext == "docx":
                import docx

                doc = docx.Document(uploaded_file)
                for table in doc.tables:
                    if len(table.rows) > 1:
                        headers = [cell.text.strip() for cell in table.rows[0].cells]
                        for row in table.rows[1:]:
                            rows.append(
                                {headers[i]: cell.text.strip() for i, cell in enumerate(row.cells) if i < len(headers)}
                            )
            elif ext in ("accdb", "mdb"):
                rows = self._parse_access_file(uploaded_file, ext, target_model)
            else:
                job.status = "FAILED"
                job.error_log = [{"row": 0, "field": "", "error": f"Unsupported file type: {ext}", "raw": ""}]
                job.completed_at = datetime.now()
                job.save()
                return Response({"error": f"Unsupported file type: {ext}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            job.status = "FAILED"
            job.error_log = [{"row": 0, "field": "", "error": f"Parse error: {e}", "raw": ""}]
            job.completed_at = datetime.now()
            job.save()
            return Response({"error": f"File parse error: {e}"}, status=status.HTTP_400_BAD_REQUEST)

        job.total_rows = len(rows)
        imported, import_errors = _import_rows(rows, target_model, job)

        for err in import_errors:
            ImportErrorModel.objects.create(
                job=job,
                row_number=err["row"],
                field_name=err.get("field", ""),
                error_message=err["error"],
                raw_value=err.get("raw", ""),
            )

        job.success_rows = imported
        job.error_rows = len(import_errors)
        job.status = "COMPLETED" if not import_errors else ("FAILED" if imported == 0 else "COMPLETED")
        job.error_log = import_errors
        job.completed_at = datetime.now()
        job.save()

        AuditLogger.log_action(
            user=request.user,
            action="IMPORT",
            resource_type="DataImport",
            resource_id=job.id,
            description=f"Imported {imported}/{job.total_rows} rows from {file_name} to {target_model}",
        )

        return Response(ImportJobSerializer(job).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="export")
    def export_data(self, request):
        target_model = request.query_params.get("model", "")
        fmt = request.query_params.get("format", "csv").lower()

        if target_model not in EXPORTABLE_MODELS:
            return Response(
                {"error": f"Invalid model. Choose from: {list(EXPORTABLE_MODELS.keys())}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        config = EXPORTABLE_MODELS[target_model]
        try:
            parts = config["model_path"].split(".")
            module = __import__(parts[0], fromlist=[parts[1]])
            for part in parts[1:]:
                module = getattr(module, part)
            model_cls = getattr(module, config["model_name"])
        except (ImportError, AttributeError) as e:
            return Response({"error": f"Model load failed: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        qs = model_cls.objects.all()
        data_fields = [f for f in config["fields"] if f != "id"]

        rows = list(qs.values(*data_fields))

        AuditLogger.log_action(
            user=request.user,
            action="EXPORT",
            resource_type="DataExport",
            description=f"Exported {len(rows)} {target_model} as {fmt.upper()}",
        )

        if fmt == "csv":
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = f'attachment; filename="{target_model}_export.csv"'
            writer = csv.DictWriter(response, fieldnames=data_fields)
            writer.writeheader()
            writer.writerows(rows)
            return response

        elif fmt == "excel" or fmt == "xlsx":
            import openpyxl

            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = target_model.title()
            ws.append(data_fields)
            for row in rows:
                ws.append([str(row.get(f, "")) for f in data_fields])
            response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response["Content-Disposition"] = f'attachment; filename="{target_model}_export.xlsx"'
            wb.save(response)
            return response

        elif fmt == "pdf":
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

            response = HttpResponse(content_type="application/pdf")
            response["Content-Disposition"] = f'attachment; filename="{target_model}_export.pdf"'

            doc = SimpleDocTemplate(response, pagesize=landscape(A4))
            elements = []
            styles = getSampleStyleSheet()
            elements.append(Paragraph(f"{target_model.title()} Export", styles["Title"]))

            table_data = [data_fields]
            for row in rows:
                table_data.append([str(row.get(f, "")) for f in data_fields])

            table = Table(table_data)
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1976d2")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("FONTSIZE", (0, 1), (-1, -1), 8),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
                    ]
                )
            )
            elements.append(table)
            doc.build(elements)
            return response

        elif fmt == "word" or fmt == "docx":
            from docx import Document

            doc = Document()
            doc.add_heading(f"{target_model.title()} Export", 0)

            table = doc.add_table(rows=1, cols=len(data_fields))
            table.style = "Light Grid Accent 1"
            for i, field in enumerate(data_fields):
                table.rows[0].cells[i].text = field

            for row in rows:
                cells = table.add_row().cells
                for i, field in enumerate(data_fields):
                    cells[i].text = str(row.get(field, ""))

            response = HttpResponse(
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            response["Content-Disposition"] = f'attachment; filename="{target_model}_export.docx"'
            doc.save(response)
            return response

        elif fmt == "json":
            data = [{k: str(v) if v is not None else "" for k, v in row.items()} for row in rows]
            response = HttpResponse(json.dumps(data, indent=2), content_type="application/json")
            response["Content-Disposition"] = f'attachment; filename="{target_model}_export.json"'
            return response

        else:
            return Response(
                {"error": f"Unsupported format: {fmt}. Use csv, excel, pdf, word, or json."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class AccessDatabaseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrTGOrDeptHead]
    pagination_class = None

    def get_serializer_class(self):
        if self.action == "list":
            return AccessDatabaseListSerializer
        return AccessDatabaseSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ("SYSADMIN", "TG_PS"):
            return AccessDatabase.objects.all()
        accessible_ids = AccessPrivilege.objects.filter(user=user).values_list("database_id", flat=True)
        return AccessDatabase.objects.filter(models.Q(id__in=accessible_ids) | models.Q(uploaded_by=user)).distinct()

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

    @action(detail=False, methods=["post"], url_path="upload")
    def upload(self, request):
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        file_name = uploaded_file.name
        ext = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""
        if ext not in ("accdb", "mdb"):
            return Response(
                {"error": "Invalid file type. Only .accdb and .mdb files are supported."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        db = AccessDatabase.objects.create(
            name=request.data.get("name", file_name),
            description=request.data.get("description", ""),
            file=uploaded_file,
            uploaded_by=request.user,
            status="PROCESSING",
        )

        AccessPrivilege.objects.create(
            database=db,
            user=request.user,
            privilege_level="ADMIN",
            granted_by=request.user,
        )

        driver = _detect_access_driver()
        if not driver:
            db.status = "ERROR"
            db.save()
            return Response(
                {"error": "No Access driver available. Install mdbtools or pyodbc.", "id": db.id},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            try:
                tables = _parse_access_tables(tmp_path, driver)
            finally:
                os.unlink(tmp_path)

            total_records = 0
            for tbl_name, rows in tables.items():
                for idx, row_data in enumerate(rows):
                    AccessTableData.objects.create(
                        database=db,
                        table_name=tbl_name,
                        row_index=idx,
                        data=row_data,
                    )
                total_records += len(rows)

            db.total_tables = len(tables)
            db.total_records = total_records
            db.status = "READY"
            db.save()

            AuditLogger.log_action(
                user=request.user,
                action="UPLOAD",
                resource_type="AccessDatabase",
                resource_id=db.id,
                description=f"Uploaded {file_name}: {len(tables)} tables, {total_records} records",
            )

            return Response(AccessDatabaseSerializer(db).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            db.status = "ERROR"
            db.save()
            return Response(
                {"error": f"Failed to parse database: {e}", "id": db.id},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["get"], url_path="tables")
    def tables(self, request, pk=None):
        db = get_object_or_404(AccessDatabase, pk=pk)
        table_names = (
            AccessTableData.objects.filter(database=db)
            .values("table_name")
            .annotate(row_count=Count("id"))
            .order_by("table_name")
        )
        return Response(list(table_names))

    @action(detail=True, methods=["get"], url_path="table-data")
    def table_data(self, request, pk=None):
        db = get_object_or_404(AccessDatabase, pk=pk)
        table_name = request.query_params.get("table", "")
        if not table_name:
            return Response({"error": "table parameter required."}, status=status.HTTP_400_BAD_REQUEST)

        sort_by = request.query_params.get("sort_by", "")
        sort_order = request.query_params.get("sort_order", "asc")

        qs = AccessTableData.objects.filter(database=db, table_name=table_name).order_by("row_index")

        if sort_by:
            if sort_order == "desc":
                qs = qs.order_by(f"-data__{sort_by}")
            else:
                qs = qs.order_by(f"data__{sort_by}")

        paginator = TableDataPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = AccessTableDataSerializer(page, many=True)

        columns = []
        first_row = qs.first()
        if first_row and isinstance(first_row.data, dict):
            columns = list(first_row.data.keys())

        response = paginator.get_paginated_response(serializer.data)
        response.data["columns"] = columns
        response.data["table_name"] = table_name
        response.data["total_rows"] = qs.count()
        return response

    @action(detail=True, methods=["post"], url_path="update-cell")
    def update_cell(self, request, pk=None):
        db = get_object_or_404(AccessDatabase, pk=pk)
        if not _has_write_permission(request.user, db):
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        table_name = request.data.get("table_name")
        row_index = request.data.get("row_index")
        column = request.data.get("column")
        value = request.data.get("value")

        if not all([table_name, row_index is not None, column]):
            return Response(
                {"error": "table_name, row_index, and column are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        row = get_object_or_404(AccessTableData, database=db, table_name=table_name, row_index=row_index)
        data = dict(row.data)
        data[column] = value
        row.data = data
        row.save()

        return Response({"ok": True, "data": row.data})

    @action(detail=True, methods=["post"], url_path="update-row")
    def update_row(self, request, pk=None):
        db = get_object_or_404(AccessDatabase, pk=pk)
        if not _has_write_permission(request.user, db):
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        table_name = request.data.get("table_name")
        row_index = request.data.get("row_index")
        data = request.data.get("data")

        if not all([table_name, row_index is not None, data]):
            return Response(
                {"error": "table_name, row_index, and data are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        row = get_object_or_404(AccessTableData, database=db, table_name=table_name, row_index=row_index)
        row.data = data
        row.save()

        return Response({"ok": True, "data": row.data})

    @action(detail=True, methods=["post"], url_path="delete-row")
    def delete_row(self, request, pk=None):
        db = get_object_or_404(AccessDatabase, pk=pk)
        if not _has_write_permission(request.user, db):
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        table_name = request.data.get("table_name")
        row_index = request.data.get("row_index")

        if not all([table_name, row_index is not None]):
            return Response(
                {"error": "table_name and row_index are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        row = get_object_or_404(AccessTableData, database=db, table_name=table_name, row_index=row_index)
        deleted_index = row.row_index
        row.delete()

        AccessTableData.objects.filter(database=db, table_name=table_name, row_index__gt=deleted_index).update(
            row_index=models.F("row_index") - 1
        )

        db.total_records = AccessTableData.objects.filter(database=db).count()
        db.save()

        return Response({"ok": True})

    @action(detail=True, methods=["post"], url_path="delete-rows")
    def delete_rows(self, request, pk=None):
        db = get_object_or_404(AccessDatabase, pk=pk)
        if not _has_write_permission(request.user, db):
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        table_name = request.data.get("table_name")
        row_indices = request.data.get("row_indices", [])

        if not table_name or not row_indices:
            return Response(
                {"error": "table_name and row_indices are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        AccessTableData.objects.filter(database=db, table_name=table_name, row_index__in=row_indices).delete()

        remaining = AccessTableData.objects.filter(database=db, table_name=table_name).order_by("row_index")
        for idx, row in enumerate(remaining):
            if row.row_index != idx:
                row.row_index = idx
                row.save(update_fields=["row_index"])

        db.total_records = AccessTableData.objects.filter(database=db).count()
        db.save()

        return Response({"ok": True, "deleted": len(row_indices)})

    @action(detail=True, methods=["post"], url_path="merge-rows")
    def merge_rows(self, request, pk=None):
        db = get_object_or_404(AccessDatabase, pk=pk)
        if not _has_write_permission(request.user, db):
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        table_name = request.data.get("table_name")
        row_indices = request.data.get("row_indices", [])
        target_index = request.data.get("target_index")

        if not all([table_name, row_indices, target_index is not None]):
            return Response(
                {"error": "table_name, row_indices, and target_index are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        rows = AccessTableData.objects.filter(database=db, table_name=table_name, row_index__in=row_indices).order_by(
            "row_index"
        )

        merged_data = {}
        for row in rows:
            if isinstance(row.data, dict):
                merged_data.update(row.data)

        target_row = get_object_or_404(AccessTableData, database=db, table_name=table_name, row_index=target_index)
        target_row.data = merged_data
        target_row.save()

        AccessTableData.objects.filter(database=db, table_name=table_name, row_index__in=row_indices).exclude(
            row_index=target_index
        ).delete()

        remaining = AccessTableData.objects.filter(database=db, table_name=table_name).order_by("row_index")
        for idx, row in enumerate(remaining):
            if row.row_index != idx:
                row.row_index = idx
                row.save(update_fields=["row_index"])

        db.total_records = AccessTableData.objects.filter(database=db).count()
        db.save()

        return Response({"ok": True, "data": target_row.data})

    @action(detail=True, methods=["post"], url_path="revert-row")
    def revert_row(self, request, pk=None):
        db = get_object_or_404(AccessDatabase, pk=pk)
        if not _has_write_permission(request.user, db):
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        table_name = request.data.get("table_name")
        row_index = request.data.get("row_index")

        if not all([table_name, row_index is not None]):
            return Response(
                {"error": "table_name and row_index are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ext = db.file.name.rsplit(".", 1)[-1].lower() if "." in db.file.name else ""
        driver = _detect_access_driver()

        if not driver:
            return Response(
                {"error": "No Access driver available to read original data."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp:
                tmp.write(db.file.read())
                tmp_path = tmp.name

            try:
                tables = _parse_access_tables(tmp_path, driver)
            finally:
                os.unlink(tmp_path)

            tbl_data = tables.get(table_name, [])
            if row_index >= len(tbl_data):
                return Response(
                    {"error": "Row index out of range in original data."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            row = get_object_or_404(AccessTableData, database=db, table_name=table_name, row_index=row_index)
            row.data = tbl_data[row_index]
            row.save()

            return Response({"ok": True, "data": row.data})

        except Exception as e:
            return Response(
                {"error": f"Failed to revert row: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"], url_path="revoke-access")
    def revoke_access(self, request, pk=None):
        db = get_object_or_404(AccessDatabase, pk=pk)
        if not _has_admin_permission(request.user, db):
            return Response({"error": "Admin permission required."}, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        deleted, _ = AccessPrivilege.objects.filter(database=db, user_id=user_id).delete()
        if deleted:
            AuditLogger.log_action(
                user=request.user,
                action="REVOKE_ACCESS",
                resource_type="AccessDatabase",
                resource_id=db.id,
                description=f"Revoked access for user {user_id}",
            )
        return Response({"ok": True, "revoked": deleted > 0})

    @action(detail=True, methods=["post"], url_path="grant-access")
    def grant_access(self, request, pk=None):
        db = get_object_or_404(AccessDatabase, pk=pk)
        if not _has_admin_permission(request.user, db):
            return Response({"error": "Admin permission required."}, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get("user_id")
        privilege_level = request.data.get("privilege_level", "VIEW")

        if not user_id:
            return Response({"error": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        from django.contrib.auth import get_user_model

        User = get_user_model()
        target_user = get_object_or_404(User, pk=user_id)

        privilege, created = AccessPrivilege.objects.update_or_create(
            database=db,
            user=target_user,
            defaults={"privilege_level": privilege_level, "granted_by": request.user},
        )

        AuditLogger.log_action(
            user=request.user,
            action="GRANT_ACCESS",
            resource_type="AccessDatabase",
            resource_id=db.id,
            description=f"{'Granted' if created else 'Updated'} {privilege_level} access for {target_user.email}",
        )

        return Response(AccessPrivilegeSerializer(privilege).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="sync-to-portal")
    def sync_to_portal(self, request, pk=None):
        db = get_object_or_404(AccessDatabase, pk=pk)
        if not _has_write_permission(request.user, db):
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        table_name = request.data.get("table", "")
        target_key = request.data.get("target_model", "")

        if not target_key or target_key not in ACCESS_SYNC_MODELS:
            return Response(
                {"error": f"Invalid target_model. Choose from: {list(ACCESS_SYNC_MODELS.keys())}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        config = ACCESS_TABLE_MAPPINGS.get(target_key, {})
        sync_config = ACCESS_SYNC_MODELS[target_key]

        all_tables = AccessTableData.objects.filter(database=db).values_list("table_name", flat=True).distinct()

        matched_table = None
        for alias in config.get("table_aliases", []):
            for t in all_tables:
                if t.lower().replace(" ", "_") == alias.lower().replace(" ", "_"):
                    matched_table = t
                    break
            if matched_table:
                break

        if not matched_table:
            matched_table = table_name if table_name in all_tables else (all_tables[0] if all_tables else None)

        if not matched_table:
            return Response({"error": "No matching table found."}, status=status.HTTP_400_BAD_REQUEST)

        rows = AccessTableData.objects.filter(database=db, table_name=matched_table).order_by("row_index")

        mapped_rows = []
        for row in rows:
            mapped_row = {}
            field_map = config.get("field_map", {})
            transforms = config.get("transforms", {})
            name_fields = config.get("name_fields", {})

            for access_col, value in row.data.items():
                access_key = access_col.lower().replace(" ", "_").replace("-", "_")
                django_field = field_map.get(access_key)
                if not django_field:
                    for fk in field_map:
                        if access_key == fk.lower():
                            django_field = fk
                            break

                if not django_field or django_field.startswith("_skip"):
                    continue

                if django_field in transforms:
                    try:
                        value = transforms[django_field](value)
                    except Exception:
                        pass

                if value is not None:
                    mapped_row[django_field] = str(value).strip() if isinstance(value, str) else value

            for field_name, aliases in name_fields.items():
                if field_name not in mapped_row:
                    for alias in aliases:
                        if alias in row.data and row.data[alias]:
                            parts = str(row.data[alias]).strip().split(" ", 1)
                            mapped_row[field_name] = parts[0]
                            if len(aliases) > 1 and len(parts) > 1:
                                mapped_row[aliases[1]] = parts[1]
                            break

            if mapped_row:
                mapped_rows.append(mapped_row)

        try:
            parts = sync_config["model_path"].split(".")
            module = __import__(parts[0], fromlist=[parts[1]])
            for part in parts[1:]:
                module = getattr(module, part)
            model_cls = getattr(module, sync_config["model_name"])
        except (ImportError, AttributeError) as e:
            return Response(
                {"error": f"Failed to load target model: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        valid_fields = {f.name for f in model_cls._meta.get_fields() if hasattr(f, "column")}
        synced = 0
        errors = []

        for idx, mapped_row in enumerate(mapped_rows):
            filtered = {k: v for k, v in mapped_row.items() if k in valid_fields and v}
            if not filtered:
                errors.append({"row": idx, "error": "No valid fields"})
                continue
            try:
                model_cls.objects.create(**filtered)
                synced += 1
            except Exception as e:
                errors.append({"row": idx, "error": str(e)})

        AuditLogger.log_action(
            user=request.user,
            action="SYNC",
            resource_type="AccessDatabase",
            resource_id=db.id,
            description=f"Synced {synced}/{len(mapped_rows)} rows from {matched_table} to {target_key}",
        )

        return Response(
            {
                "synced": synced,
                "total": len(mapped_rows),
                "errors": errors,
                "table_used": matched_table,
                "target_model": target_key,
            }
        )

    @action(detail=True, methods=["get"], url_path="export")
    def export(self, request, pk=None):
        db = get_object_or_404(AccessDatabase, pk=pk)
        table_name = request.query_params.get("table", "")
        fmt = request.query_params.get("format", "csv").lower()

        if not table_name:
            return Response({"error": "table parameter required."}, status=status.HTTP_400_BAD_REQUEST)

        rows = AccessTableData.objects.filter(database=db, table_name=table_name).order_by("row_index")

        if not rows.exists():
            return Response({"error": "Table has no data."}, status=status.HTTP_400_BAD_REQUEST)

        columns = list(rows.first().data.keys()) if rows.first().data else []

        if fmt == "csv":
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = f'attachment; filename="{table_name}_export.csv"'
            writer = csv.DictWriter(response, fieldnames=columns)
            writer.writeheader()
            for row in rows:
                writer.writerow(row.data)
            return response

        elif fmt in ("excel", "xlsx"):
            import openpyxl

            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = table_name
            ws.append(columns)
            for row in rows:
                ws.append([str(row.data.get(c, "")) for c in columns])
            response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response["Content-Disposition"] = f'attachment; filename="{table_name}_export.xlsx"'
            wb.save(response)
            return response

        elif fmt == "json":
            data = [row.data for row in rows]
            response = HttpResponse(json.dumps(data, indent=2), content_type="application/json")
            response["Content-Disposition"] = f'attachment; filename="{table_name}_export.json"'
            return response

        else:
            return Response(
                {"error": f"Unsupported format: {fmt}. Use csv, xlsx, or json."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["post"], url_path="spreadsheet-ops")
    def spreadsheet_ops(self, request, pk=None):
        db = get_object_or_404(AccessDatabase, pk=pk)
        if not _has_write_permission(request.user, db):
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        operation = request.data.get("operation")
        table_name = request.data.get("table_name")
        column = request.data.get("column", "")

        if not all([operation, table_name]):
            return Response(
                {"error": "operation and table_name are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AccessTableDataSerializer()
        qs = AccessTableData.objects.filter(database=db, table_name=table_name).order_by("row_index")
        data = list(qs.values("id", "database", "table_name", "row_index", "data"))

        if operation == "sort":
            ascending = request.data.get("ascending", True)
            data = serializer.sort_data(data, column, ascending)
            for idx, item in enumerate(data):
                row = AccessTableData.objects.get(pk=item["id"])
                row.row_index = idx
                row.save(update_fields=["row_index"])

        elif operation == "filter":
            value = request.data.get("value", "")
            data = serializer.filter_data(data, column, value)
            return Response(data)

        elif operation == "find_replace":
            find = request.data.get("find", "")
            replace = request.data.get("replace", "")
            data = serializer.find_replace(data, column, find, replace)
            for item in data:
                row = AccessTableData.objects.get(pk=item["id"])
                row.data = item.get("data", {})
                row.save(update_fields=["data"])

        elif operation == "fill_down":
            data = serializer.fill_down(data, column)
            for item in data:
                row = AccessTableData.objects.get(pk=item["id"])
                row.data = item.get("data", {})
                row.save(update_fields=["data"])

        elif operation == "copy_column":
            target_column = request.data.get("target_column", "")
            if not target_column:
                return Response(
                    {"error": "target_column is required for copy_column."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            data = serializer.copy_column(data, column, target_column)
            for item in data:
                row = AccessTableData.objects.get(pk=item["id"])
                row.data = item.get("data", {})
                row.save(update_fields=["data"])

        else:
            return Response(
                {
                    "error": f"Unknown operation: {operation}. Use sort, filter, find_replace, fill_down, or copy_column."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"ok": True, "operation": operation, "affected_rows": len(data)})
