from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model


class FileCategory(models.TextChoices):
    ADMIN = 'ADMIN', 'Administrative'
    ACAD = 'ACAD', 'Academic'
    FIN = 'FIN', 'Finance'
    INSP = 'INSP', 'Inspection'
    DISC = 'DISC', 'Discipline'
    COCC = 'COCC', 'Co-curricular'
    POL = 'POL', 'Policy'
    CORR = 'CORR', 'Correspondence'
    PROC = 'PROC', 'Procurement'


class FileType(models.TextChoices):
    CORRESPONDENCE = 'CORRESPONDENCE', 'Correspondence'
    MEMO = 'MEMO', 'Memo'
    CIRCULAR = 'CIRCULAR', 'Circular'
    REPORT = 'REPORT', 'Report'
    MINUTES = 'MINUTES', 'Minutes'
    POLICY = 'POLICY', 'Policy'
    CONTRACT = 'CONTRACT', 'Contract'
    INVOICE = 'INVOICE', 'Invoice'
    RECEIPT = 'RECEIPT', 'Receipt'
    OTHER = 'OTHER', 'Other'


class FileStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Draft'
    ACTIVE = 'ACTIVE', 'Active'
    PENDING = 'PENDING', 'Pending'
    IN_TRANSIT = 'IN_TRANSIT', 'In Transit'
    UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
    APPROVED = 'APPROVED', 'Approved'
    REJECTED = 'REJECTED', 'Rejected'
    CLOSED = 'CLOSED', 'Closed'
    ARCHIVED = 'ARCHIVED', 'Archived'


class SecurityClassification(models.TextChoices):
    PUBLIC = 'PUBLIC', 'Public'
    CONFIDENTIAL = 'CONFIDENTIAL', 'Confidential'
    RESTRICTED = 'RESTRICTED', 'Restricted'
    TOP_SECRET = 'TOP_SECRET', 'Top Secret'


class File(models.Model):
    file_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=300)
    file_type = models.CharField(max_length=20, choices=FileType.choices)
    file_category = models.CharField(max_length=20, choices=FileCategory.choices, default='ADMIN')
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_files'
    )
    current_holder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='held_files'
    )
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='files'
    )
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='files'
    )
    status = models.CharField(max_length=20, choices=FileStatus.choices, default='DRAFT')
    classification = models.CharField(max_length=20, choices=SecurityClassification.choices, default='CONFIDENTIAL')
    priority = models.CharField(max_length=20, choices=[
        ('LOW', 'Low'),
        ('NORMAL', 'Normal'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ], default='NORMAL')
    due_date = models.DateField(null=True, blank=True)
    tags = models.JSONField(default=list)
    status_timeline = models.JSONField(default=list, blank=True,
        help_text='List of {timestamp, status, changed_by_id, changed_by_name, notes} entries')
    expected_completion_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['file_number']),
            models.Index(fields=['file_type']),
            models.Index(fields=['status']),
            models.Index(fields=['created_by']),
            models.Index(fields=['current_holder']),
        ]
    
    def __str__(self):
        return f"{self.file_number} - {self.title}"


class FileMovement(models.Model):
    class Action(models.TextChoices):
        CREATED = 'CREATED', 'Created'
        SUBMITTED = 'SUBMITTED', 'Submitted'
        REVIEWED = 'REVIEWED', 'Reviewed'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        FORWARDED = 'FORWARDED', 'Forwarded'
        RETURNED = 'RETURNED', 'Returned'
        ESCALATED = 'ESCALATED', 'Escalated'
        COMMENTED = 'COMMENTED', 'Commented'
        ARCHIVED = 'ARCHIVED', 'Archived'
        DELETED = 'DELETED', 'Deleted'

    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='movements')
    from_holder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='file_movements_from'
    )
    to_holder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='file_movements_to'
    )
    action = models.CharField(max_length=20, choices=Action.choices)
    remarks = models.TextField(blank=True)
    expected_return_date = models.DateField(null=True, blank=True)
    actual_return_date = models.DateField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)
    completion_notes = models.TextField(blank=True)
    movement_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-movement_date']
        verbose_name_plural = 'file movements'
        indexes = [
            models.Index(fields=['file']),
            models.Index(fields=['from_holder']),
            models.Index(fields=['to_holder']),
            models.Index(fields=['movement_date']),
        ]
    
    def __str__(self):
        return f"{self.file.file_number} - {self.from_holder.get_full_name()} to {self.to_holder.get_full_name() if self.to_holder else 'N/A'}"


class FileAttachment(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='attachments')
    document = models.FileField(upload_to='files/attachments/')
    original_filename = models.CharField(max_length=300)
    file_size = models.IntegerField(default=0)
    mime_type = models.CharField(max_length=100, blank=True)
    file_format = models.CharField(max_length=20, blank=True, choices=[
        ('doc', 'DOC'), ('docx', 'DOCX'), ('xls', 'XLS'), ('xlsx', 'XLSX'),
        ('pdf', 'PDF'), ('jpeg', 'JPEG'), ('png', 'PNG'), ('csv', 'CSV'),
        ('txt', 'TXT'), ('other', 'Other'),
    ])
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_attachments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.original_filename


class FileComment(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='file_comments'
    )
    content = models.TextField()
    is_internal = models.BooleanField(default=False, help_text='Internal comments not visible to external stakeholders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.file.file_number} - {self.author.get_full_name()}"


class WorkflowConfig(models.Model):
    """Configurable workflow deadlines and rules per step."""
    DIRECTION_CHOICES = [
        ('INCOMING', 'Incoming'),
        ('OUTGOING', 'Outgoing'),
        ('INTERNAL', 'Internal'),
    ]
    
    step_name = models.CharField(max_length=100)
    direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES, default='INCOMING')
    default_deadline_hours = models.IntegerField(default=24)
    escalation_level = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    notification_enabled = models.BooleanField(default=True)
    notification_reminder_hours = models.IntegerField(default=4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['step_name', 'direction'],
                name='unique_step_direction'
            )
        ]
        ordering = ['direction', 'step_name']

    def __str__(self):
        return f"{self.step_name} ({self.direction}) - {self.default_deadline_hours}h"


class FileTemplate(models.Model):
    """Reusable file templates for quick file creation."""
    CATEGORY_CHOICES = [
        ('CORRESPONDENCE', 'Correspondence'),
        ('MEMO', 'Memo'),
        ('CIRCULAR', 'Circular'),
        ('REPORT', 'Report'),
        ('POLICY', 'Policy'),
        ('CONTRACT', 'Contract'),
        ('FINANCIAL', 'Financial'),
        ('INSPECTION', 'Inspection'),
        ('OTHER', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHER')
    file_type = models.CharField(max_length=50, blank=True)
    file_category = models.CharField(max_length=20, blank=True)
    default_department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='file_templates'
    )
    default_classification = models.CharField(
        max_length=20,
        choices=[('PUBLIC', 'Public'), ('INTERNAL', 'Internal'), ('CONFIDENTIAL', 'Confidential'), ('RESTRICTED', 'Restricted')],
        default='INTERNAL'
    )
    default_priority = models.CharField(
        max_length=20,
        choices=[('LOW', 'Low'), ('NORMAL', 'Normal'), ('HIGH', 'High'), ('URGENT', 'Urgent')],
        default='NORMAL'
    )
    template_content = models.TextField(blank=True, help_text='Default content/body for files created from this template')
    template_fields = models.JSONField(default=dict, blank=True, help_text='JSON schema for required fields when using this template')
    is_active = models.BooleanField(default=True)
    usage_count = models.IntegerField(default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_file_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-usage_count', 'name']

    def __str__(self):
        return f"{self.name} ({self.category})"


class OfflineQueue(models.Model):
    """Queue for offline sync operations from mobile."""
    ACTION_TYPES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('MOVE', 'Move'),
        ('ARCHIVE', 'Archive'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    object_id = models.CharField(max_length=100)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='offline_queue')
    data = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    attempt_count = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"{self.action_type} - {self.object_id} ({self.status})"


class FileClassification(models.Model):
    """AI-powered file classification results."""
    file = models.OneToOneField(File, on_delete=models.CASCADE, related_name='ai_classification')
    suggested_department = models.CharField(max_length=50, blank=True)
    department_confidence = models.FloatField(default=0)
    urgency = models.CharField(max_length=20, choices=[
        ('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High'), ('URGENT', 'Urgent'),
    ], default='MEDIUM')
    sensitivity = models.CharField(max_length=20, choices=[
        ('PUBLIC', 'Public'), ('PRIVATE', 'Private'), ('RESTRICTED', 'Restricted'),
    ], default='PUBLIC')
    file_type_suggestion = models.CharField(max_length=50, blank=True)
    keywords = models.JSONField(default=list)
    overall_confidence = models.FloatField(default=0)
    classified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'file classifications'

    def __str__(self):
        return f"Classification for {self.file.file_number}"
