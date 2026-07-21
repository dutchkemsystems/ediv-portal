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
