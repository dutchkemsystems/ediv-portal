from django.db import models
from django.conf import settings


class RiskLevel(models.TextChoices):
    LOW = 'LOW', 'Low Risk'
    MEDIUM = 'MEDIUM', 'Medium Risk'
    HIGH = 'HIGH', 'High Risk'
    CRITICAL = 'CRITICAL', 'Critical Risk'


class InterventionStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    COMPLETED = 'COMPLETED', 'Completed'
    CANCELLED = 'CANCELLED', 'Cancelled'


class StudentRiskProfile(models.Model):
    """AI-computed risk profile for each student."""
    student = models.OneToOneField(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='risk_profile'
    )
    risk_score = models.FloatField(default=0.0, help_text='0-100 risk score')
    risk_level = models.CharField(max_length=10, choices=RiskLevel.choices, default=RiskLevel.LOW)
    attendance_risk = models.FloatField(default=0.0, help_text='Risk from attendance patterns')
    academic_risk = models.FloatField(default=0.0, help_text='Risk from grade trends')
    discipline_risk = models.FloatField(default=0.0, help_text='Risk from disciplinary records')
    financial_risk = models.FloatField(default=0.0, help_text='Risk from fee payment patterns')
    engagement_risk = models.FloatField(default=0.0, help_text='Risk from participation levels')
    risk_factors = models.JSONField(default=list, blank=True, help_text='List of identified risk factors')
    recommendations = models.JSONField(default=list, blank=True, help_text='AI-generated intervention recommendations')
    last_analyzed = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-risk_score']
        indexes = [
            models.Index(fields=['risk_level']),
            models.Index(fields=['-risk_score']),
            models.Index(fields=['last_analyzed']),
        ]

    def __str__(self):
        return f"{self.student} - {self.risk_level} ({self.risk_score:.1f}%)"


class EarlyWarningAlert(models.Model):
    """Triggered when a student crosses a risk threshold."""
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='early_warnings'
    )
    risk_profile = models.ForeignKey(
        StudentRiskProfile,
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    alert_type = models.CharField(max_length=30, choices=[
        ('ATTENDANCE_DROP', 'Attendance Drop'),
        ('GRADE_DECLINE', 'Grade Decline'),
        ('DISCIPLINE_SPIKE', 'Discipline Spike'),
        ('FEE_DEFAULT', 'Fee Default'),
        ('DROPOUT_RISK', 'Dropout Risk'),
        ('ABSENCE_STREAK', 'Absence Streak'),
    ])
    risk_level = models.CharField(max_length=10, choices=RiskLevel.choices)
    message = models.TextField()
    details = models.JSONField(default=dict, blank=True)
    acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='acknowledged_warnings'
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['alert_type', 'acknowledged']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"ALERT: {self.student} - {self.alert_type} ({self.risk_level})"


class Intervention(models.Model):
    """Recommended or taken action for at-risk students."""
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='interventions'
    )
    alert = models.ForeignKey(
        EarlyWarningAlert,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='interventions'
    )
    intervention_type = models.CharField(max_length=30, choices=[
        ('COUNSELING', 'Counseling Session'),
        ('PARENT_MEETING', 'Parent Meeting'),
        ('ACADEMIC_SUPPORT', 'Academic Support'),
        ('FINANCIAL_AID', 'Financial Aid'),
        ('MENTORING', 'Mentoring Program'),
        ('DISCIPLINE_REVIEW', 'Discipline Review'),
        ('SCHEDULE_ADJUSTMENT', 'Schedule Adjustment'),
        ('PEER_SUPPORT', 'Peer Support'),
        ('CUSTOM', 'Custom Intervention'),
    ])
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_interventions'
    )
    status = models.CharField(max_length=15, choices=InterventionStatus.choices, default=InterventionStatus.PENDING)
    outcome = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student} - {self.title} ({self.status})"


class RiskTrend(models.Model):
    """Historical risk score snapshots for trend analysis."""
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='risk_trends'
    )
    risk_score = models.FloatField()
    risk_level = models.CharField(max_length=10, choices=RiskLevel.choices)
    attendance_risk = models.FloatField(default=0.0)
    academic_risk = models.FloatField(default=0.0)
    discipline_risk = models.FloatField(default=0.0)
    financial_risk = models.FloatField(default=0.0)
    snapshot_date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-snapshot_date']
        unique_together = ['student', 'snapshot_date']

    def __str__(self):
        return f"{self.student} - {self.snapshot_date} - {self.risk_level}"
