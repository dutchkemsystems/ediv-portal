"""Extension Plan Feature B: registry service — audit trail, follow-ups, export, workflow hand-off."""

import csv

from django.http import HttpResponse

from apps.registry.models import Document, DocumentAuditEntry, FollowUp


def record_document_audit(document, action, user=None, details=""):
    """Append an entry to a document's audit trail."""
    return DocumentAuditEntry.objects.create(
        document=document,
        action=action,
        user=user,
        details=details,
    )


def create_follow_up(document, assignee, created_by, due_date=None, notes=""):
    """Create a follow-up record for a document."""
    return FollowUp.objects.create(
        document=document,
        assignee=assignee,
        created_by=created_by,
        due_date=due_date,
        notes=notes,
    )


def assign_document_to_workflow(document, action_required="Process", deadline=None):
    """Hand off a document to the workflows automation (creates a workflow Task)."""
    from apps.workflows.automation import MailDistributor

    return MailDistributor().assign_action(
        mail=document,
        action_required=action_required,
        deadline=deadline,
    )


def export_documents(fmt="csv"):
    """Export the registry index (CSV/XLSX/JSON). Mirrors data_import_export export actions."""
    rows = Document.objects.order_by("-created_at").values(
        "reference_number",
        "title",
        "document_type",
        "status",
        "classification",
        "version",
        "created_at",
        "updated_at",
    )
    if fmt == "csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="registry_export.csv"'
        writer = csv.DictWriter(
            response, fieldnames=list(rows.first().keys()) if rows.first() else []
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
        return response
    if fmt in ("excel", "xlsx"):
        import openpyxl

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Registry"
        first = rows.first()
        if first:
            columns = list(first.keys())
            ws.append(columns)
            for row in rows:
                ws.append([str(row.get(c, "")) for c in columns])
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="registry_export.xlsx"'
        wb.save(response)
        return response
    if fmt == "json":
        import json

        data = list(rows)
        response = HttpResponse(
            json.dumps(data, indent=2, default=str), content_type="application/json"
        )
        response["Content-Disposition"] = 'attachment; filename="registry_export.json"'
        return response
    return HttpResponse(
        "Unsupported format. Use csv, xlsx, or json.",
        status=400,
        content_type="text/plain",
    )
