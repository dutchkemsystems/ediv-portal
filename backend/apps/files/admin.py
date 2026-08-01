from django.contrib import admin
from .models import (
    File, FileMovement, FileAttachment, FileComment,
    WorkflowConfig, FileTemplate, OfflineQueue, FileClassification,
)


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ['file_number', 'title', 'file_type', 'created_by', 'current_holder', 'status', 'priority']
    list_filter = ['file_type', 'status', 'classification', 'priority']
    search_fields = ['file_number', 'title', 'description']
    raw_id_fields = ['created_by', 'current_holder', 'department', 'school']


@admin.register(FileMovement)
class FileMovementAdmin(admin.ModelAdmin):
    list_display = ['file', 'from_holder', 'to_holder', 'action', 'movement_date', 'is_returned']
    list_filter = ['is_returned']
    raw_id_fields = ['file', 'from_holder', 'to_holder']


@admin.register(FileAttachment)
class FileAttachmentAdmin(admin.ModelAdmin):
    list_display = ['file', 'original_filename', 'file_size', 'mime_type', 'file_format', 'uploaded_by', 'created_at']
    raw_id_fields = ['file', 'uploaded_by']


@admin.register(FileComment)
class FileCommentAdmin(admin.ModelAdmin):
    list_display = ['file', 'author', 'created_at']
    raw_id_fields = ['file', 'author']


@admin.register(WorkflowConfig)
class WorkflowConfigAdmin(admin.ModelAdmin):
    list_display = ['step_name', 'direction', 'default_deadline_hours', 'escalation_level', 'is_active']
    list_filter = ['direction', 'is_active', 'notification_enabled']
    search_fields = ['step_name']


@admin.register(FileTemplate)
class FileTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'file_type', 'default_priority', 'usage_count', 'is_active', 'created_by']
    list_filter = ['category', 'is_active', 'default_classification', 'default_priority']
    search_fields = ['name', 'description']
    raw_id_fields = ['created_by', 'default_department']


@admin.register(OfflineQueue)
class OfflineQueueAdmin(admin.ModelAdmin):
    list_display = ['action_type', 'object_id', 'user', 'status', 'attempt_count', 'created_at']
    list_filter = ['action_type', 'status']
    search_fields = ['object_id', 'error_message']
    raw_id_fields = ['user']


@admin.register(FileClassification)
class FileClassificationAdmin(admin.ModelAdmin):
    list_display = ['file', 'suggested_department', 'department_confidence', 'urgency', 'sensitivity', 'overall_confidence']
    list_filter = ['urgency', 'sensitivity']
    search_fields = ['file__file_number', 'suggested_department']
    raw_id_fields = ['file']
