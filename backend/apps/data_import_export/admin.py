from django.contrib import admin
from .models import ImportJob, ImportError


@admin.register(ImportJob)
class ImportJobAdmin(admin.ModelAdmin):
    list_display = ['id', 'file_name', 'file_type', 'status', 'total_rows', 'success_rows', 'error_rows', 'created_by', 'created_at']
    list_filter = ['file_type', 'status']


@admin.register(ImportError)
class ImportErrorAdmin(admin.ModelAdmin):
    list_display = ['id', 'job', 'row_number', 'field_name', 'error_message']
    list_filter = ['job']
