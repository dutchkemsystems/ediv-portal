from django.db import models
from django.conf import settings


class IncomingMail(models.Model):
    class Status(models.TextChoices):
        RECEIVED = 'RECEIVED', 'Received'
        SCANNED = 'SCANNED', 'Scanned'
        CLASSIFIED = 'CLASSIFIED', 'Classified'
        ASSIGNED = 'ASSIGNED', 'Assigned'
        UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
        IN_ACTION = 'IN_ACTION', 'In Action'
        RESPONDED = 'RESPONDED', 'Responded'
        DISPATCHED = 'DISPATCHED', 'Dispatched'
        ARCHIVED = 'ARCHIVED', 'Archived'

    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        NORMAL = 'NORMAL', 'Normal'
        HIGH = 'HIGH', 'High'
        URGENT = 'URGENT', 'Urgent'

    class Classification(models.TextChoices):
        PUBLIC = 'PUBLIC', 'Public'
        INTERNAL = 'INTERNAL', 'Internal'
        CONFIDENTIAL = 'CONFIDENTIAL', 'Confidential'
        RESTRICTED = 'RESTRICTED', 'Restricted'

    class SubjectCategory(models.TextChoices):
        LETTER = 'LETTER', 'Letter'
        MEMO = 'MEMO', 'Memo'
        CIRCULAR = 'CIRCULAR', 'Circular'
        INVITE = 'INVITE', 'Invitation'
        COMPLAINT = 'COMPLAINT', 'Complaint'
        OTHER = 'OTHER', 'Other'

    mail_number = models.CharField(max_length=50, unique=True)
    sender_name = models.CharField(max_length=200)
    sender_organization = models.CharField(max_length=300, blank=True)
    subject = models.CharField(max_length=300)
    date_received = models.DateField()
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_mails'
    )
    department = models.ForeignKey(
        'departments.Department', on_delete=models.SET_NULL, null=True, blank=True, related_name='incoming_mails'
    )
    classification = models.CharField(max_length=20, choices=Classification.choices, default='INTERNAL')
    priority = models.CharField(max_length=20, choices=Priority.choices, default='NORMAL')
    subject_category = models.CharField(max_length=20, choices=SubjectCategory.choices, default='OTHER')
    status = models.CharField(max_length=20, choices=Status.choices, default='RECEIVED')
    scanned_copy = models.FileField(upload_to='mail/scans/', blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['mail_number']),
            models.Index(fields=['status']),
            models.Index(fields=['date_received']),
        ]

    def __str__(self):
        return f"{self.mail_number} - {self.subject}"


class MailScanRecord(models.Model):
    mail = models.ForeignKey(IncomingMail, on_delete=models.CASCADE, related_name='scan_records')
    scanned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    scan_date = models.DateTimeField(auto_now_add=True)
    scan_notes = models.TextField(blank=True)
    attachment_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-scan_date']

    def __str__(self):
        return f"Scan of {self.mail.mail_number}"


class MailAssignment(models.Model):
    class Status(models.TextChoices):
        ASSIGNED = 'ASSIGNED', 'Assigned'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'

    mail = models.ForeignKey(IncomingMail, on_delete=models.CASCADE, related_name='assignments')
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mail_assignments_made')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mail_assignments_received')
    assignment_date = models.DateTimeField(auto_now_add=True)
    action_required = models.TextField()
    deadline = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default='ASSIGNED')
    response_notes = models.TextField(blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-assignment_date']

    def __str__(self):
        return f"{self.mail.mail_number} -> {self.assigned_to.get_full_name()}"


class MailMovement(models.Model):
    mail = models.ForeignKey(IncomingMail, on_delete=models.CASCADE, related_name='movements')
    from_person = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mail_sent')
    to_person = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mail_received')
    action = models.CharField(max_length=100)
    remarks = models.TextField(blank=True)
    movement_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-movement_date']
        verbose_name_plural = 'mail movements'

    def __str__(self):
        return f"{self.mail.mail_number}: {self.from_person.get_full_name()} -> {self.to_person.get_full_name()}"
