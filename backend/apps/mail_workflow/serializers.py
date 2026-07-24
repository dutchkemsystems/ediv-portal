from rest_framework import serializers
from .models import IncomingMail, MailScanRecord, MailAssignment, MailMovement


class MailScanRecordSerializer(serializers.ModelSerializer):
    scanned_by_name = serializers.SerializerMethodField()

    class Meta:
        model = MailScanRecord
        fields = ['id', 'mail', 'scanned_by', 'scanned_by_name', 'scan_date', 'scan_notes', 'attachment_count']
        read_only_fields = ['id', 'scan_date']

    def get_scanned_by_name(self, obj):
        return obj.scanned_by.get_full_name()


class MailAssignmentSerializer(serializers.ModelSerializer):
    assigned_by_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()

    class Meta:
        model = MailAssignment
        fields = ['id', 'mail', 'assigned_by', 'assigned_by_name', 'assigned_to', 'assigned_to_name',
                  'assignment_date', 'action_required', 'deadline', 'status', 'response_notes', 'completed_date']
        read_only_fields = ['id', 'assignment_date']

    def get_assigned_by_name(self, obj):
        return obj.assigned_by.get_full_name()

    def get_assigned_to_name(self, obj):
        return obj.assigned_to.get_full_name()


class MailMovementSerializer(serializers.ModelSerializer):
    from_person_name = serializers.SerializerMethodField()
    to_person_name = serializers.SerializerMethodField()

    class Meta:
        model = MailMovement
        fields = ['id', 'mail', 'from_person', 'from_person_name', 'to_person', 'to_person_name',
                  'action', 'remarks', 'movement_date']
        read_only_fields = ['id', 'movement_date']

    def get_from_person_name(self, obj):
        return obj.from_person.get_full_name()

    def get_to_person_name(self, obj):
        return obj.to_person.get_full_name()


class IncomingMailSerializer(serializers.ModelSerializer):
    received_by_name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    scan_records = MailScanRecordSerializer(many=True, read_only=True)
    assignments = MailAssignmentSerializer(many=True, read_only=True)
    movements = MailMovementSerializer(many=True, read_only=True)

    class Meta:
        model = IncomingMail
        fields = ['id', 'mail_number', 'sender_name', 'sender_organization', 'subject',
                  'date_received', 'received_by', 'received_by_name', 'department', 'department_name',
                  'classification', 'priority', 'subject_category', 'status', 'scanned_copy', 'notes',
                  'scan_records', 'assignments', 'movements', 'created_at', 'updated_at']
        read_only_fields = ['id', 'mail_number', 'created_at', 'updated_at']

    def get_received_by_name(self, obj):
        return obj.received_by.get_full_name()

    def get_department_name(self, obj):
        if obj.department:
            return obj.department.name
        return None


class IncomingMailListSerializer(serializers.ModelSerializer):
    received_by_name = serializers.SerializerMethodField()

    class Meta:
        model = IncomingMail
        fields = ['id', 'mail_number', 'sender_name', 'subject', 'date_received', 'received_by_name',
                  'classification', 'priority', 'subject_category', 'status', 'created_at']

    def get_received_by_name(self, obj):
        return obj.received_by.get_full_name()
