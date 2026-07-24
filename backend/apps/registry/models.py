from django.db import models
from django.conf import settings


class DocumentType(models.TextChoices):
    CORRESPONDENCE = 'CORRESPONDENCE', 'Correspondence'
    MEMO = 'MEMO', 'Memo'
    CIRCULAR = 'CIRCULAR', 'Circular'
    REPORT = 'REPORT', 'Report'
    MINUTES = 'MINUTES', 'Minutes'
    POLICY = 'POLICY', 'Policy'
    CONTRACT = 'CONTRACT', 'Contract'
    LETTER = 'LETTER', 'Letter'
    OTHER = 'OTHER', 'Other'


class DocumentStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Draft'
    PENDING = 'PENDING', 'Pending'
    APPROVED = 'APPROVED', 'Approved'
    REJECTED = 'REJECTED', 'Rejected'
    ARCHIVED = 'ARCHIVED', 'Archived'


class Document(models.Model):
    reference_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=300)
    document_type = models.CharField(max_length=20, choices=DocumentType.choices)
    content = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_documents'
    )
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents'
    )
    status = models.CharField(max_length=20, choices=DocumentStatus.choices, default='DRAFT')
    classification = models.CharField(max_length=20, choices=[
        ('PUBLIC', 'Public'),
        ('INTERNAL', 'Internal'),
        ('CONFIDENTIAL', 'Confidential'),
        ('RESTRICTED', 'Restricted'),
    ], default='INTERNAL')
    version = models.IntegerField(default=1)
    effective_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['reference_number']),
            models.Index(fields=['document_type']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.reference_number} - {self.title}"


class Correspondence(models.Model):
    class Direction(models.TextChoices):
        INCOMING = 'INCOMING', 'Incoming'
        OUTGOING = 'OUTGOING', 'Outgoing'
        INTERNAL = 'INTERNAL', 'Internal'
    
    document = models.OneToOneField(Document, on_delete=models.CASCADE, related_name='correspondence')
    direction = models.CharField(max_length=20, choices=Direction.choices)
    sender = models.CharField(max_length=200)
    recipient = models.CharField(max_length=200)
    date_received = models.DateField()
    date_sent = models.DateField(null=True, blank=True)
    subject = models.CharField(max_length=300)
    is_urgent = models.BooleanField(default=False)
    requires_response = models.BooleanField(default=False)
    response_deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_received']
    
    def __str__(self):
        return f"{self.direction} - {self.subject}"


class Filing(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='filings')
    file_code = models.CharField(max_length=50)
    box_number = models.CharField(max_length=20, blank=True)
    shelf_number = models.CharField(max_length=20, blank=True)
    room = models.CharField(max_length=100, blank=True)
    filed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='filed_documents'
    )
    filed_date = models.DateField()
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-filed_date']
    
    def __str__(self):
        return f"{self.document.reference_number} - {self.file_code}"


class DocumentVersion(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField()
    content = models.TextField()
    file = models.FileField(upload_to='registry/versions/')
    changes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='document_versions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['document', 'version_number']
        ordering = ['-version_number']
    
    def __str__(self):
        return f"{self.document.reference_number} - v{self.version_number}"


class MemoWorkflow(models.Model):
    class WorkflowType(models.TextChoices):
        MEMO = 'MEMO', 'Memo'
        CIRCULAR = 'CIRCULAR', 'Circular'

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        REGISTERED = 'REGISTERED', 'Registered'
        UNDER_APPROVAL = 'UNDER_APPROVAL', 'Under Approval'
        CIRCULATING = 'CIRCULATING', 'Circulating'
        ACKNOWLEDGED = 'ACKNOWLEDGED', 'Acknowledged'
        IN_ACTION = 'IN_ACTION', 'In Action'
        REPORTED = 'REPORTED', 'Reported'
        ARCHIVED = 'ARCHIVED', 'Archived'

    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='memo_workflows')
    workflow_type = models.CharField(max_length=20, choices=WorkflowType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default='DRAFT')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.workflow_type} - {self.document.reference_number}"


class MemoApproval(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    memo_workflow = models.ForeignKey(MemoWorkflow, on_delete=models.CASCADE, related_name='approvals')
    approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='memo_approvals')
    approval_order = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=Status.choices, default='PENDING')
    comments = models.TextField(blank=True)
    approved_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['approval_order']

    def __str__(self):
        return f"{self.memo_workflow} - {self.approver.get_full_name()}"


class MemoCirculation(models.Model):
    class Status(models.TextChoices):
        SENT = 'SENT', 'Sent'
        ACKNOWLEDGED = 'ACKNOWLEDGED', 'Acknowledged'
        ACTION_TAKEN = 'ACTION_TAKEN', 'Action Taken'
        REPORTED = 'REPORTED', 'Reported'

    memo_workflow = models.ForeignKey(MemoWorkflow, on_delete=models.CASCADE, related_name='circulations')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='memo_circulations')
    date_sent = models.DateTimeField(auto_now_add=True)
    date_acknowledged = models.DateTimeField(null=True, blank=True)
    acknowledgement_notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default='SENT')

    class Meta:
        ordering = ['-date_sent']

    def __str__(self):
        return f"{self.memo_workflow} -> {self.recipient.get_full_name()}"
