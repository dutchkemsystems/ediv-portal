from django.contrib import admin

from .models import (
    IncomingMail,
    MailAssignment,
    MailCorrespondence,
    MailCorrespondenceMovement,
    MailMovement,
    MailScanRecord,
    OutgoingMail,
    OutgoingMailApproval,
    OutgoingMailMovement,
    SchoolHQCorrespondence,
    SchoolHQCorrespondenceMovement,
)


@admin.register(IncomingMail)
class IncomingMailAdmin(admin.ModelAdmin):
    list_display = ["mail_number", "sender_name", "subject", "status", "received_by", "date_received"]
    list_filter = ["status", "classification", "priority"]
    search_fields = ["mail_number", "sender_name", "subject"]
    raw_id_fields = ["received_by", "department"]


@admin.register(MailScanRecord)
class MailScanRecordAdmin(admin.ModelAdmin):
    list_display = ["mail", "scanned_by", "scan_date", "attachment_count"]
    raw_id_fields = ["mail", "scanned_by"]


@admin.register(MailAssignment)
class MailAssignmentAdmin(admin.ModelAdmin):
    list_display = ["mail", "assigned_by", "assigned_to", "status", "assignment_date"]
    list_filter = ["status"]
    raw_id_fields = ["mail", "assigned_by", "assigned_to"]


@admin.register(MailMovement)
class MailMovementAdmin(admin.ModelAdmin):
    list_display = ["mail", "from_person", "to_person", "action", "movement_date"]
    raw_id_fields = ["mail", "from_person", "to_person"]


@admin.register(OutgoingMail)
class OutgoingMailAdmin(admin.ModelAdmin):
    list_display = ["mail_number", "subject", "recipient_name", "status", "created_by", "date_created"]
    list_filter = ["status", "classification", "priority"]
    search_fields = ["mail_number", "subject", "recipient_name"]
    raw_id_fields = ["created_by", "department"]


@admin.register(OutgoingMailApproval)
class OutgoingMailApprovalAdmin(admin.ModelAdmin):
    list_display = ["outgoing_mail", "approver", "status", "approved_date"]
    list_filter = ["status"]
    raw_id_fields = ["outgoing_mail", "approver"]


@admin.register(OutgoingMailMovement)
class OutgoingMailMovementAdmin(admin.ModelAdmin):
    list_display = ["outgoing_mail", "from_person", "to_person", "action", "movement_date"]
    raw_id_fields = ["outgoing_mail", "from_person", "to_person"]


@admin.register(SchoolHQCorrespondence)
class SchoolHQCorrespondenceAdmin(admin.ModelAdmin):
    list_display = ["reference_number", "direction", "subject", "status", "sender"]
    list_filter = ["direction", "status"]
    search_fields = ["reference_number", "subject"]
    raw_id_fields = ["sender", "recipient", "school", "department"]


@admin.register(SchoolHQCorrespondenceMovement)
class SchoolHQCorrespondenceMovementAdmin(admin.ModelAdmin):
    list_display = ["correspondence", "from_person", "to_person", "action", "movement_date"]
    raw_id_fields = ["correspondence", "from_person", "to_person"]


@admin.register(MailCorrespondence)
class MailCorrespondenceAdmin(admin.ModelAdmin):
    list_display = ["reference_number", "correspondence_type", "subject", "status", "sender"]
    list_filter = ["correspondence_type", "status"]
    search_fields = ["reference_number", "subject"]
    raw_id_fields = ["sender", "recipient", "department", "school"]


@admin.register(MailCorrespondenceMovement)
class MailCorrespondenceMovementAdmin(admin.ModelAdmin):
    list_display = ["correspondence", "from_person", "to_person", "action", "movement_date"]
    raw_id_fields = ["correspondence", "from_person", "to_person"]
