from django.db import models
from django.conf import settings


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
    ACTIVE = 'ACTIVE', 'Active'
    PENDING = 'PENDING', 'Pending'
    IN_TRANSIT = 'IN_TRANSIT', 'In Transit'
    ARCHIVED = 'ARCHIVED', 'Archived'
    CONFIDENTIAL = 'CONFIDENTIAL', 'Confidential'


class File(models.Model):
    file_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=300)
    file_type = models.CharField(max_length=20, choices=FileType.choices)
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
    status = models.CharField(max_length=20, choices=FileStatus.choices, default='ACTIVE')
    classification = models.CharField(max_length=20, choices=[
        ('PUBLIC', 'Public'),
        ('INTERNAL', 'Internal'),
        ('CONFIDENTIAL', 'Confidential'),
        ('RESTRICTED', 'Restricted'),
    ], default='INTERNAL')
    priority = models.CharField(max_length=20, choices=[
        ('LOW', 'Low'),
        ('NORMAL', 'Normal'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ], default='NORMAL')
    due_date = models.DateField(null=True, blank=True)
    tags = models.JSONField(default=list)
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
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='movements')
    from_holder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='file_movements_from'
    )
    to_holder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='file_movements_to'
    )
    action = models.CharField(max_length=100)
    remarks = models.TextField(blank=True)
    expected_return_date = models.DateField(null=True, blank=True)
    actual_return_date = models.DateField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)
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
        return f"{self.file.file_number} - {self.from_holder.get_full_name()} to {self.to_holder.get_full_name()}"


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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.file.file_number} - {self.author.get_full_name()}"
