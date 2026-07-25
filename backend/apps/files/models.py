from django.db import models
from django.conf import settings


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
