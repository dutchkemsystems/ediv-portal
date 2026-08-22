from django.contrib import admin

from .models import Correspondence, Document, DocumentVersion, Filing, MemoApproval, MemoCirculation, MemoWorkflow


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["reference_number", "title", "document_type", "created_by", "status", "classification"]
    list_filter = ["document_type", "status", "classification"]
    search_fields = ["reference_number", "title"]
    raw_id_fields = ["created_by", "department"]


@admin.register(Correspondence)
class CorrespondenceAdmin(admin.ModelAdmin):
    list_display = ["document", "direction", "sender", "recipient", "date_received", "is_urgent"]
    list_filter = ["direction", "is_urgent", "requires_response"]
    raw_id_fields = ["document"]


@admin.register(Filing)
class FilingAdmin(admin.ModelAdmin):
    list_display = ["document", "file_code", "box_number", "shelf_number", "filed_by", "filed_date"]
    search_fields = ["file_code"]
    raw_id_fields = ["document", "filed_by"]


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ["document", "version_number", "created_by", "created_at"]
    raw_id_fields = ["document", "created_by"]


@admin.register(MemoWorkflow)
class MemoWorkflowAdmin(admin.ModelAdmin):
    list_display = ["workflow_type", "document", "status", "created_at"]
    list_filter = ["workflow_type", "status"]
    raw_id_fields = ["document"]


@admin.register(MemoApproval)
class MemoApprovalAdmin(admin.ModelAdmin):
    list_display = ["memo_workflow", "approver", "approval_order", "status", "approved_date"]
    list_filter = ["status"]
    raw_id_fields = ["memo_workflow", "approver"]


@admin.register(MemoCirculation)
class MemoCirculationAdmin(admin.ModelAdmin):
    list_display = ["memo_workflow", "recipient", "date_sent", "date_acknowledged", "status"]
    list_filter = ["status"]
    raw_id_fields = ["memo_workflow", "recipient"]
