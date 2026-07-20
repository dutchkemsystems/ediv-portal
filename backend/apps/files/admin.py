from django.contrib import admin
from .models import File, FileMovement, FileAttachment, FileComment


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
    list_display = ['file', 'original_filename', 'file_size', 'uploaded_by', 'created_at']
    raw_id_fields = ['file', 'uploaded_by']


@admin.register(FileComment)
class FileCommentAdmin(admin.ModelAdmin):
    list_display = ['file', 'author', 'created_at']
    raw_id_fields = ['file', 'author']
