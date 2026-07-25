from rest_framework import serializers
from .models import (
    IncomingMail, MailScanRecord, MailAssignment, MailMovement,
    OutgoingMail, OutgoingMailApproval, OutgoingMailMovement,
    SchoolHQCorrespondence, SchoolHQCorrespondenceMovement,
    MailCorrespondence, MailCorrespondenceMovement
)


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


class OutgoingMailApprovalSerializer(serializers.ModelSerializer):
    approver_name = serializers.SerializerMethodField()

    class Meta:
        model = OutgoingMailApproval
        fields = ['id', 'outgoing_mail', 'approver', 'approver_name', 'approval_order', 'status', 'comments', 'approved_date']
        read_only_fields = ['id', 'approved_date']

    def get_approver_name(self, obj):
        return obj.approver.get_full_name()


class OutgoingMailMovementSerializer(serializers.ModelSerializer):
    from_person_name = serializers.SerializerMethodField()
    to_person_name = serializers.SerializerMethodField()

    class Meta:
        model = OutgoingMailMovement
        fields = ['id', 'outgoing_mail', 'from_person', 'from_person_name', 'to_person', 'to_person_name',
                  'action', 'remarks', 'movement_date']
        read_only_fields = ['id', 'movement_date']

    def get_from_person_name(self, obj):
        return obj.from_person.get_full_name()

    def get_to_person_name(self, obj):
        if obj.to_person:
            return obj.to_person.get_full_name()
        return None


class OutgoingMailSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    approvals = OutgoingMailApprovalSerializer(many=True, read_only=True)
    movements = OutgoingMailMovementSerializer(many=True, read_only=True)

    class Meta:
        model = OutgoingMail
        fields = ['id', 'mail_number', 'subject', 'recipient_name', 'recipient_organization',
                  'recipient_address', 'date_created', 'date_dispatched', 'date_delivered',
                  'created_by', 'created_by_name', 'department', 'department_name',
                  'classification', 'priority', 'status', 'content', 'notes', 'scanned_copy',
                  'approvals', 'movements', 'created_at', 'updated_at']
        read_only_fields = ['id', 'mail_number', 'date_created', 'created_at', 'updated_at']

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name()

    def get_department_name(self, obj):
        if obj.department:
            return obj.department.name
        return None


class OutgoingMailListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = OutgoingMail
        fields = ['id', 'mail_number', 'subject', 'recipient_name', 'date_created',
                  'created_by_name', 'classification', 'priority', 'status', 'created_at']

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name()


class SchoolHQCorrespondenceMovementSerializer(serializers.ModelSerializer):
    from_person_name = serializers.SerializerMethodField()
    to_person_name = serializers.SerializerMethodField()

    class Meta:
        model = SchoolHQCorrespondenceMovement
        fields = ['id', 'correspondence', 'from_person', 'from_person_name', 'to_person', 'to_person_name',
                  'action', 'remarks', 'movement_date']
        read_only_fields = ['id', 'movement_date']

    def get_from_person_name(self, obj):
        return obj.from_person.get_full_name()

    def get_to_person_name(self, obj):
        if obj.to_person:
            return obj.to_person.get_full_name()
        return None


class SchoolHQCorrespondenceSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    recipient_name_display = serializers.SerializerMethodField()
    school_name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    movements = SchoolHQCorrespondenceMovementSerializer(many=True, read_only=True)

    class Meta:
        model = SchoolHQCorrespondence
        fields = ['id', 'reference_number', 'direction', 'subject', 'school', 'school_name',
                  'department', 'department_name', 'sender', 'sender_name', 'recipient', 'recipient_name_display',
                  'date_created', 'date_submitted', 'date_received', 'date_resolved',
                  'classification', 'priority', 'status', 'content', 'response',
                  'requires_response', 'response_deadline', 'movements', 'created_at', 'updated_at']
        read_only_fields = ['id', 'reference_number', 'date_created', 'created_at', 'updated_at']

    def get_sender_name(self, obj):
        return obj.sender.get_full_name()

    def get_recipient_name_display(self, obj):
        if obj.recipient:
            return obj.recipient.get_full_name()
        return None

    def get_school_name(self, obj):
        if obj.school:
            return obj.school.name
        return None

    def get_department_name(self, obj):
        if obj.department:
            return obj.department.name
        return None


class SchoolHQCorrespondenceListSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    school_name = serializers.SerializerMethodField()

    class Meta:
        model = SchoolHQCorrespondence
        fields = ['id', 'reference_number', 'direction', 'subject', 'sender_name', 'school_name',
                  'classification', 'priority', 'status', 'date_created', 'created_at']

    def get_sender_name(self, obj):
        return obj.sender.get_full_name()

    def get_school_name(self, obj):
        if obj.school:
            return obj.school.name
        return None


class MailCorrespondenceMovementSerializer(serializers.ModelSerializer):
    from_person_name = serializers.SerializerMethodField()
    to_person_name = serializers.SerializerMethodField()

    class Meta:
        model = MailCorrespondenceMovement
        fields = ['id', 'correspondence', 'from_person', 'from_person_name', 'to_person', 'to_person_name',
                  'action', 'remarks', 'movement_date']
        read_only_fields = ['id', 'movement_date']

    def get_from_person_name(self, obj):
        return obj.from_person.get_full_name()

    def get_to_person_name(self, obj):
        if obj.to_person:
            return obj.to_person.get_full_name()
        return None


class MailCorrespondenceSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    recipient_name_display = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    school_name = serializers.SerializerMethodField()
    movements = MailCorrespondenceMovementSerializer(many=True, read_only=True)

    class Meta:
        model = MailCorrespondence
        fields = ['id', 'reference_number', 'correspondence_type', 'subject',
                  'sender', 'sender_name', 'recipient', 'recipient_name_display',
                  'department', 'department_name', 'school', 'school_name',
                  'date_created', 'date_sent', 'date_received', 'status',
                  'classification', 'priority', 'notes', 'movements', 'created_at', 'updated_at']
        read_only_fields = ['id', 'reference_number', 'date_created', 'created_at', 'updated_at']

    def get_sender_name(self, obj):
        return obj.sender.get_full_name()

    def get_recipient_name_display(self, obj):
        if obj.recipient:
            return obj.recipient.get_full_name()
        return None

    def get_department_name(self, obj):
        if obj.department:
            return obj.department.name
        return None

    def get_school_name(self, obj):
        if obj.school:
            return obj.school.name
        return None


class MailCorrespondenceListSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = MailCorrespondence
        fields = ['id', 'reference_number', 'correspondence_type', 'subject', 'sender_name',
                  'status', 'classification', 'priority', 'date_created', 'created_at']

    def get_sender_name(self, obj):
        return obj.sender.get_full_name()
