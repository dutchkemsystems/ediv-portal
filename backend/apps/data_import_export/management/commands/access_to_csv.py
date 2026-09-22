import csv
import json
import os
import subprocess
import sys
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.data_import_export.access_mapping import ACCESS_TABLE_MAPPINGS, find_mapping_for_table


class Command(BaseCommand):
    help = "Convert a Microsoft Access database to CSV files for portal import"

    def add_arguments(self, parser):
        parser.add_argument("db_path", help="Path to .accdb or .mdb file")
        parser.add_argument("--output", "-o", default="export", help="Output directory (default: export)")
        parser.add_argument(
            "--list-tables",
            action="store_true",
            help="List tables without exporting",
        )
        parser.add_argument("--table", "-t", help="Export only this specific table")
        parser.add_argument(
            "--driver",
            choices=["pyodbc", "mdbtools"],
            help="Force a specific driver",
        )

    def handle(self, *args, **options):
        db_path = Path(options["db_path"]).resolve()
        if not db_path.exists():
            raise CommandError(f"Database not found: {db_path}")

        if options["driver"]:
            driver = options["driver"]
            if driver == "pyodbc":
                try:
                    import pyodbc

                    pyodbc.connect(f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path};")
                except Exception as e:
                    raise CommandError(f"pyodbc not available: {e}")
            else:
                if not self._check_mdbtools():
                    raise CommandError("mdb-tools not found on this system")
        else:
            driver = self._detect_driver()
            if driver is None:
                raise CommandError(
                    "No suitable driver found. Install pyodbc with Access ODBC driver on Windows, "
                    "or mdb-tools on Linux."
                )

        self.stdout.write(f"Using driver: {driver}")

        if driver == "pyodbc":
            tables = self._list_tables_pyodbc(db_path)
        else:
            tables = self._list_tables_mdbtools(db_path)

        self.stdout.write(f"Found {len(tables)} tables in database")

        if options["list_tables"]:
            for table in sorted(tables):
                mapping = find_mapping_for_table(table)
                status = "MAPPED" if mapping else "unmapped"
                target = mapping["model"] if mapping else "-"
                self.stdout.write(f"  {table} -> {target} [{status}]")
            return

        output_dir = Path(options["output"])
        output_dir.mkdir(parents=True, exist_ok=True)

        export_tables = tables
        if options["table"]:
            target = options["table"]
            if target not in tables:
                raise CommandError(f"Table '{target}' not found. Available: {', '.join(sorted(tables))}")
            export_tables = [target]

        manifest = {
            "source": str(db_path),
            "driver": driver,
            "tables": [],
        }

        exported_count = 0
        skipped_count = 0

        for table in sorted(export_tables):
            mapping = find_mapping_for_table(table)
            if mapping is None:
                self.stdout.write(self.style.WARNING(f"  Skipping unmapped table: {table}"))
                skipped_count += 1
                continue

            self.stdout.write(f"  Exporting: {table} -> {mapping['model']}")

            try:
                if driver == "pyodbc":
                    headers, rows = self._export_table_pyodbc(db_path, table)
                else:
                    headers, rows = self._export_table_mdbtools(db_path, table)
            except Exception as e:
                self.stderr.write(f"  Error exporting {table}: {e}")
                skipped_count += 1
                continue

            if not rows:
                self.stdout.write(f"    Empty table, skipping")
                skipped_count += 1
                continue

            mapped_headers, mapped_rows = self._apply_field_mapping(rows, headers, mapping)

            csv_filename = f"{mapping['model']}.csv"
            csv_path = output_dir / csv_filename

            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(mapped_headers)
                writer.writerows(mapped_rows)

            manifest["tables"].append(
                {
                    "source_table": table,
                    "model": mapping["model"],
                    "csv_file": csv_filename,
                    "row_count": len(mapped_rows),
                    "columns": mapped_headers,
                }
            )

            self.stdout.write(self.style.SUCCESS(f"    Exported {len(mapped_rows)} rows to {csv_path}"))
            exported_count += 1

        manifest_path = output_dir / "manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Done: {exported_count} exported, {skipped_count} skipped. " f"Manifest: {manifest_path}"
            )
        )

    def _detect_driver(self):
        if sys.platform == "win32":
            try:
                import pyodbc

                conn_str = "DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
                pyodbc.connect(conn_str)
                return "pyodbc"
            except Exception:
                return None
        else:
            if self._check_mdbtools():
                return "mdbtools"
            return None

    def _check_mdbtools(self):
        try:
            result = subprocess.run(
                ["mdb-tables", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _list_tables_pyodbc(self, db_path):
        import pyodbc

        conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path};"
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        tables = []
        for row in cursor.tables(tableType="TABLE"):
            name = row.table_name
            if not name.startswith("MSys"):
                tables.append(name)
        conn.close()
        return tables

    def _list_tables_mdbtools(self, db_path):
        result = subprocess.run(
            ["mdb-tables", "-1", str(db_path)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise CommandError(f"mdb-tables failed: {result.stderr}")
        tables = [t.strip() for t in result.stdout.strip().split("\n") if t.strip()]
        return tables

    def _export_table_pyodbc(self, db_path, table):
        import pyodbc

        conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path};"
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM [{table}]")
        headers = [desc[0] for desc in cursor.description]
        rows = [list(row) for row in cursor.fetchall()]
        conn.close()
        return headers, rows

    def _export_table_mdbtools(self, db_path, table):
        result = subprocess.run(
            ["mdb-export", str(db_path), table],
            capture_output=True,
            text=True,
            encoding="utf-8-sig",
        )
        if result.returncode != 0:
            raise CommandError(f"mdb-export failed for {table}: {result.stderr}")
        reader = csv.reader(result.stdout.splitlines())
        all_rows = list(reader)
        if not all_rows:
            return [], []
        headers = all_rows[0]
        rows = all_rows[1:]
        return headers, rows

    def _apply_field_mapping(self, rows, headers, mapping):
        field_map = mapping.get("field_map", {})
        transforms = mapping.get("transforms", {})
        name_fields = mapping.get("name_fields", {})

        new_headers = []
        header_indices = {}
        for i, h in enumerate(headers):
            header_indices[h.lower()] = i

        for target_field, source_field in field_map.items():
            new_headers.append(target_field)

        mapped_rows = []
        for row in rows:
            new_row = []
            for target_field, source_field in field_map.items():
                src_lower = source_field.lower()
                if src_lower in header_indices:
                    val = row[header_indices[src_lower]]
                else:
                    val = ""
                if target_field in transforms:
                    val = transforms[target_field](val) if callable(transforms[target_field]) else val
                new_row.append(val)
            mapped_rows.append(new_row)

        if name_fields:
            full_name_field = name_fields.get("full_name")
            first_field = name_fields.get("first_name", "first_name")
            last_field = name_fields.get("last_name", "last_name")

            if full_name_field and first_field in field_map and last_field in field_map:
                try:
                    fn_idx = new_headers.index(first_field)
                    ln_idx = new_headers.index(last_field)
                except ValueError:
                    fn_idx = None
                    ln_idx = None

                if fn_idx is not None and ln_idx is not None:
                    full_src = field_map.get(first_field) or field_map.get(last_field)
                    full_src_lower = full_src.lower() if full_src else None
                    if full_src_lower and full_src_lower in header_indices:
                        src_idx = header_indices[full_src_lower]
                        for row in mapped_rows:
                            full_name = row[fn_idx] if fn_idx < len(row) else ""
                            if full_name:
                                parts = full_name.split(" ", 1)
                                row[fn_idx] = parts[0]
                                row[ln_idx] = parts[1] if len(parts) > 1 else ""
                            else:
                                row[fn_idx] = ""
                                row[ln_idx] = ""

        for field_name, source_field in name_fields.items():
            if field_name in ("first_name", "last_name"):
                continue
            src_lower = source_field.lower()
            if src_lower not in header_indices:
                continue
            if field_name in field_map:
                continue
            new_headers.append(field_name)
            src_idx = header_indices[src_lower]
            for row in mapped_rows:
                val = row[src_idx] if src_idx < len(row) else ""
                row.append(val)

        for src_field, target_field in transforms.items():
            if target_field in new_headers:
                continue
            if src_field in [f for f in field_map.values()]:
                src_lower = src_field.lower()
                if src_lower in header_indices:
                    new_headers.append(src_lower)
                    src_idx = header_indices[src_lower]
                    for row in mapped_rows:
                        val = row[src_idx] if src_idx < len(row) else ""
                        val = transforms[src_field](val) if callable(transforms[src_field]) else val
                        row.append(val)

        return new_headers, mapped_rows
