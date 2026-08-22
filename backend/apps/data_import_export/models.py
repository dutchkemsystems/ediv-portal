from django.conf import settings
from django.db import models


class ImportJob(models.Model):
    class FileType(models.TextChoices):
        CSV = "CSV", "CSV"
        EXCEL = "EXCEL", "Excel"
        PDF = "PDF", "PDF"
        WORD = "WORD", "Word"
        JSON = "JSON", "JSON"
        ACCESS = "ACCESS", "Microsoft Access"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    file_name = models.CharField(max_length=300)
    file_type = models.CharField(max_length=10, choices=FileType.choices)
    target_model = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=Status.choices, default="PENDING")
    total_rows = models.IntegerField(default=0)
    success_rows = models.IntegerField(default=0)
    error_rows = models.IntegerField(default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="import_jobs")
    error_log = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.file_name} ({self.status})"


class ImportError(models.Model):
    job = models.ForeignKey(ImportJob, on_delete=models.CASCADE, related_name="errors")
    row_number = models.IntegerField()
    field_name = models.CharField(max_length=100, blank=True)
    error_message = models.TextField()
    raw_value = models.TextField(blank=True)

    class Meta:
        ordering = ["row_number"]

    def __str__(self):
        return f"Row {self.row_number}: {self.error_message}"


class AccessDatabase(models.Model):
    class Status(models.TextChoices):
        UPLOADED = "UPLOADED", "Uploaded"
        PROCESSING = "PROCESSING", "Processing"
        READY = "READY", "Ready"
        ERROR = "ERROR", "Error"

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="access_databases/")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="access_databases")
    status = models.CharField(max_length=20, choices=Status.choices, default="UPLOADED")
    total_tables = models.IntegerField(default=0)
    total_records = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.status})"


class AccessTableData(models.Model):
    database = models.ForeignKey(AccessDatabase, on_delete=models.CASCADE, related_name="table_data")
    table_name = models.CharField(max_length=200)
    row_index = models.IntegerField()
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["database", "table_name", "row_index"]
        ordering = ["table_name", "row_index"]

    def __str__(self):
        return f"{self.database.name}.{self.table_name} row {self.row_index}"


class AccessPrivilege(models.Model):
    class PrivilegeLevel(models.TextChoices):
        VIEW = "VIEW", "View"
        EDIT = "EDIT", "Edit"
        DELETE = "DELETE", "Delete"
        ADMIN = "ADMIN", "Admin"

    database = models.ForeignKey(AccessDatabase, on_delete=models.CASCADE, related_name="privileges")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="access_privileges")
    privilege_level = models.CharField(max_length=10, choices=PrivilegeLevel.choices, default="VIEW")
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="granted_access_privileges"
    )
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["database", "user"]
        ordering = ["-granted_at"]

    def __str__(self):
        return f"{self.user.email} -> {self.database.name} ({self.privilege_level})"
