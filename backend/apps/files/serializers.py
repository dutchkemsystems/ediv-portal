from rest_framework import serializers
from .models import File, FileMovement, FileAttachment, FileComment


class FileCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    
    class Meta:
        model = FileComment
        fields = ['id', 'file', 'author', 'author_name', 'content', 'created_at', 'updated_at']
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
                  'is_returned', 'movement_date']
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
        fields = ['id', 'file_number', 'title', 'file_type', 'description',
                  'created_by', 'created_by_name', 'current_holder', 'current_holder_name',
                  'department', 'department_name', 'school', 'school_name',
                  'status', 'classification', 'priority', 'due_date', 'tags',
                  'movements', 'attachments', 'comments', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name()
    
    def get_current_holder_name(self, obj):
        if obj.current_holder:
            return obj.current_holder.get_full_name()
        return None
    
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
        fields = ['id', 'file_number', 'title', 'file_type', 'created_by_name',
                  'current_holder_name', 'status', 'priority', 'created_at']
    
    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name()
    
    def get_current_holder_name(self, obj):
        if obj.current_holder:
            return obj.current_holder.get_full_name()
        return None

