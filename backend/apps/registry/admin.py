from django.contrib import admin
from .models import Document, Correspondence, Filing, DocumentVersion


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['reference_number', 'title', 'document_type', 'created_by', 'status', 'classification']
    list_filter = ['document_type', 'status', 'classification']
    search_fields = ['reference_number', 'title']
    raw_id_fields = ['created_by', 'department']


@admin.register(Correspondence)
class CorrespondenceAdmin(admin.ModelAdmin):
    list_display = ['document', 'direction', 'sender', 'recipient', 'date_received', 'is_urgent']
    list_filter = ['direction', 'is_urgent', 'requires_response']
    raw_id_fields = ['document']


@admin.register(Filing)
class FilingAdmin(admin.ModelAdmin):
    list_display = ['document', 'file_code', 'box_number', 'shelf_number', 'filed_by', 'filed_date']
    search_fields = ['file_code']
    raw_id_fields = ['document', 'filed_by']


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ['document', 'version_number', 'created_by', 'created_at']
    raw_id_fields = ['document', 'created_by']
