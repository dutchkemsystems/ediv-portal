from django.db import models
from django.conf import settings


class AuditAction(models.TextChoices):
    LOGIN = 'LOGIN', 'User Login'
    LOGOUT = 'LOGOUT', 'User Logout'
    CREATE = 'CREATE', 'Record Created'
    READ = 'READ', 'Record Viewed'
    UPDATE = 'UPDATE', 'Record Updated'
    DELETE = 'DELETE', 'Record Deleted'
    EXPORT = 'EXPORT', 'Data Exported'
    IMPORT = 'IMPORT', 'Data Imported'
    APPROVE = 'APPROVE', 'Record Approved'
    REJECT = 'REJECT', 'Record Rejected'
    PASSWORD_CHANGE = 'PASSWORD_CHANGE', 'Password Changed'
    MFA_ENABLE = 'MFA_ENABLE', 'MFA Enabled'
    MFA_DISABLE = 'MFA_DISABLE', 'MFA Disabled'
    SETTINGS_CHANGE = 'SETTINGS_CHANGE', 'Settings Changed'
    FILE_MOVEMENT = 'FILE_MOVEMENT', 'File Movement'


class AuditLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=20, choices=AuditAction.choices)
    module = models.CharField(max_length=50)
    object_type = models.CharField(max_length=100, blank=True)
    object_id = models.CharField(max_length=50, blank=True)
    object_repr = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['action']),
            models.Index(fields=['module']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user} - {self.action} - {self.module} at {self.created_at}"


class ComplianceStatus(models.TextChoices):
    COMPLIANT = 'COMPLIANT', 'Compliant'
    NON_COMPLIANT = 'NON_COMPLIANT', 'Non-Compliant'
    PARTIAL = 'PARTIAL', 'Partially Compliant'
    PENDING_REVIEW = 'PENDING_REVIEW', 'Pending Review'
    UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'


class ComplianceCategory(models.TextChoices):
    FINANCIAL = 'FINANCIAL', 'Financial Compliance'
    ACADEMIC = 'ACADEMIC', 'Academic Compliance'
    ADMINISTRATIVE = 'ADMINISTRATIVE', 'Administrative Compliance'
    REGULATORY = 'REGULATORY', 'Regulatory Compliance'
    SAFETY = 'SAFETY', 'Safety & Security'
    DATA_PROTECTION = 'DATA_PROTECTION', 'Data Protection'
    PROCUREMENT = 'PROCUREMENT', 'Procurement Compliance'
    HR = 'HR', 'Human Resources Compliance'


class ComplianceItem(models.Model):
    category = models.CharField(max_length=20, choices=ComplianceCategory.choices)
    title = models.CharField(max_length=200)
    description = models.TextField()
    reference_document = models.CharField(max_length=200, blank=True)
    frequency = models.CharField(max_length=50, help_text='e.g., Annual, Quarterly, Monthly')
    is_mandatory = models.BooleanField(default=True)
    applies_to = models.JSONField(default=list, help_text='List of roles or departments this applies to')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'title']

    def __str__(self):
        return f"[{self.category}] {self.title}"


class ComplianceRecord(models.Model):
    item = models.ForeignKey(ComplianceItem, on_delete=models.CASCADE, related_name='records')
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, null=True, blank=True, related_name='compliance_records')
    department = models.ForeignKey('departments.Department', on_delete=models.CASCADE, null=True, blank=True, related_name='compliance_records')
    status = models.CharField(max_length=20, choices=ComplianceStatus.choices, default='PENDING_REVIEW')
    academic_year = models.CharField(max_length=9)
    due_date = models.DateField()
    completion_date = models.DateField(null=True, blank=True)
    evidence = models.TextField(blank=True, help_text='Description of evidence provided')
    evidence_file = models.FileField(upload_to='compliance/evidence/', blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_compliance'
    )
    review_date = models.DateField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    findings = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    next_review_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_compliance'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-due_date']

    def __str__(self):
        return f"{self.item.title} - {self.status}"


class ViolationSeverity(models.TextChoices):
    LOW = 'LOW', 'Low'
    MEDIUM = 'MEDIUM', 'Medium'
    HIGH = 'HIGH', 'High'
    CRITICAL = 'CRITICAL', 'Critical'


class ViolationStatus(models.TextChoices):
    OPEN = 'OPEN', 'Open'
    INVESTIGATING = 'INVESTIGATING', 'Investigating'
    RESOLVED = 'RESOLVED', 'Resolved'
    ESCALATED = 'ESCALATED', 'Escalated'
    CLOSED = 'CLOSED', 'Closed'


class Violation(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(max_length=10, choices=ViolationSeverity.choices, default='MEDIUM')
    status = models.CharField(max_length=15, choices=ViolationStatus.choices, default='OPEN')
    category = models.CharField(max_length=20, choices=ComplianceCategory.choices)
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, null=True, blank=True, related_name='violations')
    department = models.ForeignKey('departments.Department', on_delete=models.CASCADE, null=True, blank=True, related_name='violations')
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reported_violations'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_violations'
    )
    incident_date = models.DateField()
    resolution_date = models.DateField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    evidence = models.TextField(blank=True)
    corrective_action = models.TextField(blank=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.severity}] {self.title}"
