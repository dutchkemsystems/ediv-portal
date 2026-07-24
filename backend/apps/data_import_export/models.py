from django.db import models
from django.conf import settings


class ImportJob(models.Model):
    class FileType(models.TextChoices):
        CSV = 'CSV', 'CSV'
        EXCEL = 'EXCEL', 'Excel'
        PDF = 'PDF', 'PDF'
        WORD = 'WORD', 'Word'
        JSON = 'JSON', 'JSON'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'

    file_name = models.CharField(max_length=300)
    file_type = models.CharField(max_length=10, choices=FileType.choices)
    target_model = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=Status.choices, default='PENDING')
    total_rows = models.IntegerField(default=0)
    success_rows = models.IntegerField(default=0)
    error_rows = models.IntegerField(default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='import_jobs'
    )
    error_log = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.file_name} ({self.status})"


class ImportError(models.Model):
    job = models.ForeignKey(ImportJob, on_delete=models.CASCADE, related_name='errors')
    row_number = models.IntegerField()
    field_name = models.CharField(max_length=100, blank=True)
    error_message = models.TextField()
    raw_value = models.TextField(blank=True)

    class Meta:
        ordering = ['row_number']

    def __str__(self):
        return f"Row {self.row_number}: {self.error_message}"
