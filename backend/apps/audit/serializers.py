from rest_framework import serializers
from .models import AuditLog, ComplianceItem, ComplianceRecord, Violation


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'user_name', 'action', 'module', 'object_type',
                  'object_id', 'object_repr', 'description', 'ip_address',
                  'old_value', 'new_value', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_user_name(self, obj):
        if obj.user:
            return obj.user.get_full_name()
        return 'System'


class AuditLogListSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = ['id', 'user_name', 'action', 'module', 'object_repr', 'created_at']

    def get_user_name(self, obj):
        if obj.user:
            return obj.user.get_full_name()
        return 'System'


class ComplianceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceItem
        fields = ['id', 'category', 'title', 'description', 'reference_document',
                  'frequency', 'is_mandatory', 'applies_to', 'is_active',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ComplianceRecordSerializer(serializers.ModelSerializer):
    item_title = serializers.SerializerMethodField()
    school_name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    reviewed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ComplianceRecord
        fields = ['id', 'item', 'item_title', 'school', 'school_name',
                  'department', 'department_name', 'status', 'academic_year',
                  'due_date', 'completion_date', 'evidence', 'reviewed_by',
                  'reviewed_by_name', 'review_date', 'review_notes',
                  'findings', 'recommendations', 'next_review_date',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_item_title(self, obj):
        return obj.item.title

    def get_school_name(self, obj):
        return obj.school.name if obj.school else None

    def get_department_name(self, obj):
        return obj.department.name if obj.department else None

    def get_reviewed_by_name(self, obj):
        if obj.reviewed_by:
            return obj.reviewed_by.get_full_name()
        return None


class ComplianceRecordListSerializer(serializers.ModelSerializer):
    item_title = serializers.SerializerMethodField()
    school_name = serializers.SerializerMethodField()

    class Meta:
        model = ComplianceRecord
        fields = ['id', 'item_title', 'school_name', 'status', 'due_date', 'academic_year']

    def get_item_title(self, obj):
        return obj.item.title

    def get_school_name(self, obj):
        return obj.school.name if obj.school else None


class ViolationSerializer(serializers.ModelSerializer):
    reported_by_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()
    school_name = serializers.SerializerMethodField()

    class Meta:
        model = Violation
        fields = ['id', 'title', 'description', 'severity', 'status', 'category',
                  'school', 'school_name', 'department', 'reported_by',
                  'reported_by_name', 'assigned_to', 'assigned_to_name',
                  'incident_date', 'resolution_date', 'resolution_notes',
                  'evidence', 'corrective_action', 'follow_up_required',
                  'follow_up_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_reported_by_name(self, obj):
        if obj.reported_by:
            return obj.reported_by.get_full_name()
        return None

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name()
        return None

    def get_school_name(self, obj):
        return obj.school.name if obj.school else None


class ViolationListSerializer(serializers.ModelSerializer):
    reported_by_name = serializers.SerializerMethodField()
    school_name = serializers.SerializerMethodField()

    class Meta:
        model = Violation
        fields = ['id', 'title', 'severity', 'status', 'category', 'school_name',
                  'reported_by_name', 'incident_date', 'created_at']

    def get_reported_by_name(self, obj):
        if obj.reported_by:
            return obj.reported_by.get_full_name()
        return None

    def get_school_name(self, obj):
        return obj.school.name if obj.school else None
