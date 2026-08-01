from rest_framework import serializers
from .models import (
    File, FileMovement, FileAttachment, FileComment,
    WorkflowConfig, FileTemplate, FileClassification, OfflineQueue,
)


class FileCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    
    class Meta:
        model = FileComment
        fields = ['id', 'file', 'author', 'author_name', 'content', 'is_internal', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_author_name(self, obj):
        return obj.author.get_full_name()


class FileAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = FileAttachment
        fields = ['id', 'file', 'document', 'original_filename', 'file_size',
                  'uploaded_by', 'uploaded_by_name', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_uploaded_by_name(self, obj):
        return obj.uploaded_by.get_full_name()


class FileMovementSerializer(serializers.ModelSerializer):
    from_holder_name = serializers.SerializerMethodField()
    to_holder_name = serializers.SerializerMethodField()
    
    class Meta:
        model = FileMovement
        fields = ['id', 'file', 'from_holder', 'from_holder_name', 'to_holder', 'to_holder_name',
                  'action', 'remarks', 'expected_return_date', 'actual_return_date',
                  'is_returned', 'completion_notes', 'movement_date']
        read_only_fields = ['id', 'movement_date']
    
    def get_from_holder_name(self, obj):
        return obj.from_holder.get_full_name()
    
    def get_to_holder_name(self, obj):
        return obj.to_holder.get_full_name()


class FileSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    current_holder_name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    school_name = serializers.SerializerMethodField()
    movements = FileMovementSerializer(many=True, read_only=True)
    attachments = FileAttachmentSerializer(many=True, read_only=True)
    comments = FileCommentSerializer(many=True, read_only=True)
    
    class Meta:
        model = File
        fields = ['id', 'file_number', 'title', 'file_type', 'file_category', 'description',
                  'created_by', 'created_by_name', 'current_holder', 'current_holder_name',
                  'department', 'department_name', 'school', 'school_name',
                  'status', 'classification', 'priority', 'due_date', 'tags',
                  'status_timeline', 'expected_completion_date',
                  'movements', 'attachments', 'comments', 'created_at', 'updated_at']
        read_only_fields = ['id', 'file_number', 'created_at', 'updated_at', 'created_by', 'status_timeline']
    
    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name()
    
    def get_current_holder_name(self, obj):
        if obj.current_holder:
            return obj.current_holder.get_full_name()
        return None


# === NEW SERIALIZERS FOR ENTERPRISE FEATURES ===

class WorkflowConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowConfig
        fields = ['id', 'step_name', 'direction', 'default_deadline_hours',
                  'escalation_level', 'is_active', 'notification_enabled',
                  'notification_reminder_hours', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class FileTemplateSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    default_department_name = serializers.SerializerMethodField()

    class Meta:
        model = FileTemplate
        fields = ['id', 'name', 'description', 'category', 'file_type', 'file_category',
                  'default_department', 'default_department_name', 'default_classification',
                  'default_priority', 'template_content', 'template_fields',
                  'is_active', 'usage_count', 'created_by', 'created_by_name',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'usage_count', 'created_at', 'updated_at']

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() or obj.created_by.username

    def get_default_department_name(self, obj):
        return obj.default_department.name if obj.default_department else None


class FileClassificationSerializer(serializers.ModelSerializer):
    file_number = serializers.CharField(source='file.file_number', read_only=True)
    file_title = serializers.CharField(source='file.title', read_only=True)

    class Meta:
        model = FileClassification
        fields = ['id', 'file', 'file_number', 'file_title', 'suggested_department',
                  'department_confidence', 'urgency', 'sensitivity', 'file_type_suggestion',
                  'keywords', 'overall_confidence', 'classified_at']
        read_only_fields = ['id', 'classified_at']


class OfflineQueueSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = OfflineQueue
        fields = ['id', 'object_id', 'action_type', 'user', 'user_name', 'data',
                  'status', 'attempt_count', 'error_message', 'created_at',
                  'updated_at', 'processed_at']
        read_only_fields = ['id', 'attempt_count', 'created_at', 'updated_at', 'processed_at']

    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    def get_department_name(self, obj):
        if obj.department:
            return obj.department.name
        return None
    
    def get_school_name(self, obj):
        if obj.school:
            return obj.school.name
        return None


class FileListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    current_holder_name = serializers.SerializerMethodField()
    
    class Meta:
        model = File
        fields = ['id', 'file_number', 'title', 'file_type', 'file_category', 'created_by_name',
                  'current_holder_name', 'status', 'classification', 'priority', 'created_at']
    
    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name()
    
    def get_current_holder_name(self, obj):
        if obj.current_holder:
            return obj.current_holder.get_full_name()
        return None

