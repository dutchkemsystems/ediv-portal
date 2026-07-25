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


class OutgoingMail(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        PENDING_APPROVAL = 'PENDING_APPROVAL', 'Pending Approval'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        DISPATCHED = 'DISPATCHED', 'Dispatched'
        DELIVERED = 'DELIVERED', 'Delivered'
        ARCHIVED = 'ARCHIVED', 'Archived'

    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        NORMAL = 'NORMAL', 'Normal'
        HIGH = 'HIGH', 'High'
        URGENT = 'URGENT', 'Urgent'

    class Classification(models.TextChoices):
        PUBLIC = 'PUBLIC', 'Public'
        CONFIDENTIAL = 'CONFIDENTIAL', 'Confidential'
        RESTRICTED = 'RESTRICTED', 'Restricted'
        TOP_SECRET = 'TOP_SECRET', 'Top Secret'

    mail_number = models.CharField(max_length=50, unique=True)
    subject = models.CharField(max_length=300)
    recipient_name = models.CharField(max_length=200)
    recipient_organization = models.CharField(max_length=300, blank=True)
    recipient_address = models.TextField(blank=True)
    date_created = models.DateField(auto_now_add=True)
    date_dispatched = models.DateField(null=True, blank=True)
    date_delivered = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_outgoing_mails'
    )
    department = models.ForeignKey(
        'departments.Department', on_delete=models.SET_NULL, null=True, blank=True, related_name='outgoing_mails'
    )
    classification = models.CharField(max_length=20, choices=Classification.choices, default='CONFIDENTIAL')
    priority = models.CharField(max_length=20, choices=Priority.choices, default='NORMAL')
    status = models.CharField(max_length=20, choices=Status.choices, default='DRAFT')
    content = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    scanned_copy = models.FileField(upload_to='mail/outgoing/scans/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['mail_number']),
            models.Index(fields=['status']),
            models.Index(fields=['date_created']),
        ]

    def __str__(self):
        return f"{self.mail_number} - {self.subject}"


class OutgoingMailApproval(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    outgoing_mail = models.ForeignKey(OutgoingMail, on_delete=models.CASCADE, related_name='approvals')
    approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='outgoing_mail_approvals')
    approval_order = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=Status.choices, default='PENDING')
    comments = models.TextField(blank=True)
    approved_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['approval_order']

    def __str__(self):
        return f"{self.outgoing_mail.mail_number} - {self.approver.get_full_name()}"


class OutgoingMailMovement(models.Model):
    outgoing_mail = models.ForeignKey(OutgoingMail, on_delete=models.CASCADE, related_name='movements')
    from_person = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='outgoing_mail_sent')
    to_person = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='outgoing_mail_received')
    action = models.CharField(max_length=100)
    remarks = models.TextField(blank=True)
    movement_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-movement_date']
        verbose_name_plural = 'outgoing mail movements'

    def __str__(self):
        return f"{self.outgoing_mail.mail_number}: {self.from_person.get_full_name()} -> {self.to_person.get_full_name() if self.to_person else 'N/A'}"


class SchoolHQCorrespondence(models.Model):
    class Direction(models.TextChoices):
        SCHOOL_TO_HQ = 'SCHOOL_TO_HQ', 'School to HQ'
        HQ_TO_SCHOOL = 'HQ_TO_SCHOOL', 'HQ to School'

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        SUBMITTED = 'SUBMITTED', 'Submitted'
        RECEIVED_AT_HQ = 'RECEIVED_AT_HQ', 'Received at HQ'
        UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        ACTION_REQUIRED = 'ACTION_REQUIRED', 'Action Required'
        COMPLETED = 'COMPLETED', 'Completed'
        ARCHIVED = 'ARCHIVED', 'Archived'

    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        NORMAL = 'NORMAL', 'Normal'
        HIGH = 'HIGH', 'High'
        URGENT = 'URGENT', 'Urgent'

    class Classification(models.TextChoices):
        PUBLIC = 'PUBLIC', 'Public'
        CONFIDENTIAL = 'CONFIDENTIAL', 'Confidential'
        RESTRICTED = 'RESTRICTED', 'Restricted'
        TOP_SECRET = 'TOP_SECRET', 'Top Secret'

    reference_number = models.CharField(max_length=50, unique=True)
    direction = models.CharField(max_length=20, choices=Direction.choices)
    subject = models.CharField(max_length=300)
    school = models.ForeignKey(
        'schools.School', on_delete=models.SET_NULL, null=True, blank=True, related_name='hq_correspondences'
    )
    department = models.ForeignKey(
        'departments.Department', on_delete=models.SET_NULL, null=True, blank=True, related_name='school_correspondences'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_hq_correspondences'
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_hq_correspondences'
    )
    date_created = models.DateField(auto_now_add=True)
    date_submitted = models.DateField(null=True, blank=True)
    date_received = models.DateField(null=True, blank=True)
    date_resolved = models.DateField(null=True, blank=True)
    classification = models.CharField(max_length=20, choices=Classification.choices, default='CONFIDENTIAL')
    priority = models.CharField(max_length=20, choices=Priority.choices, default='NORMAL')
    status = models.CharField(max_length=20, choices=Status.choices, default='DRAFT')
    content = models.TextField(blank=True)
    response = models.TextField(blank=True)
    requires_response = models.BooleanField(default=False)
    response_deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['reference_number']),
            models.Index(fields=['direction']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.reference_number} - {self.subject}"


class SchoolHQCorrespondenceMovement(models.Model):
    correspondence = models.ForeignKey(SchoolHQCorrespondence, on_delete=models.CASCADE, related_name='movements')
    from_person = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hq_correspondence_sent')
    to_person = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='hq_correspondence_received')
    action = models.CharField(max_length=100)
    remarks = models.TextField(blank=True)
    movement_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-movement_date']
        verbose_name_plural = 'school HQ correspondence movements'

    def __str__(self):
        return f"{self.correspondence.reference_number}: {self.from_person.get_full_name()} -> {self.to_person.get_full_name() if self.to_person else 'N/A'}"


class MailCorrespondence(models.Model):
    class CorrespondenceType(models.TextChoices):
        INCOMING = 'INCOMING', 'Incoming'
        OUTGOING = 'OUTGOING', 'Outgoing'
        INTERNAL = 'INTERNAL', 'Internal'
        SCHOOL_HQ = 'SCHOOL_HQ', 'School-HQ'
        HQ_SCHOOL = 'HQ_SCHOOL', 'HQ-School'
        DEPARTMENT = 'DEPARTMENT', 'Department'

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        REGISTERED = 'REGISTERED', 'Registered'
        IN_TRANSIT = 'IN_TRANSIT', 'In Transit'
        RECEIVED = 'RECEIVED', 'Received'
        UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
        ACTION_REQUIRED = 'ACTION_REQUIRED', 'Action Required'
        COMPLETED = 'COMPLETED', 'Completed'
        ARCHIVED = 'ARCHIVED', 'Archived'

    reference_number = models.CharField(max_length=50, unique=True)
    correspondence_type = models.CharField(max_length=20, choices=CorrespondenceType.choices)
    subject = models.CharField(max_length=300)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_correspondences'
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_correspondences'
    )
    department = models.ForeignKey(
        'departments.Department', on_delete=models.SET_NULL, null=True, blank=True, related_name='correspondences'
    )
    school = models.ForeignKey(
        'schools.School', on_delete=models.SET_NULL, null=True, blank=True, related_name='correspondences'
    )
    date_created = models.DateField(auto_now_add=True)
    date_sent = models.DateField(null=True, blank=True)
    date_received = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default='DRAFT')
    classification = models.CharField(max_length=20, choices=[
        ('PUBLIC', 'Public'),
        ('CONFIDENTIAL', 'Confidential'),
        ('RESTRICTED', 'Restricted'),
        ('TOP_SECRET', 'Top Secret'),
    ], default='CONFIDENTIAL')
    priority = models.CharField(max_length=20, choices=[
        ('LOW', 'Low'),
        ('NORMAL', 'Normal'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ], default='NORMAL')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['reference_number']),
            models.Index(fields=['correspondence_type']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.reference_number} - {self.subject}"


class MailCorrespondenceMovement(models.Model):
    correspondence = models.ForeignKey(MailCorrespondence, on_delete=models.CASCADE, related_name='movements')
    from_person = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='correspondence_sent')
    to_person = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='correspondence_received')
    action = models.CharField(max_length=100)
    remarks = models.TextField(blank=True)
    movement_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-movement_date']
        verbose_name_plural = 'mail correspondence movements'

    def __str__(self):
        return f"{self.correspondence.reference_number}: {self.from_person.get_full_name()} -> {self.to_person.get_full_name() if self.to_person else 'N/A'}"
