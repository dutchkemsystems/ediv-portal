from django.db import models
from django.conf import settings


class ReportType(models.TextChoices):
    ENROLLMENT = 'ENROLLMENT', 'Enrollment Report'
    ATTENDANCE = 'ATTENDANCE', 'Attendance Report'
    ACADEMIC = 'ACADEMIC', 'Academic Report'
    FINANCIAL = 'FINANCIAL', 'Financial Report'
    STAFF = 'STAFF', 'Staff Report'
    INFRASTRUCTURE = 'INFRASTRUCTURE', 'Infrastructure Report'


class AnalyticsReport(models.Model):
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=ReportType.choices)
    description = models.TextField(blank=True)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='analytics_reports'
    )
    parameters = models.JSONField(default=dict)
    data = models.JSONField(default=dict)
    file = models.FileField(upload_to='analytics/reports/', blank=True)
    is_scheduled = models.BooleanField(default=False)
    schedule_frequency = models.CharField(max_length=20, choices=[
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('YEARLY', 'Yearly'),
    ], blank=True)
    last_generated = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report_type']),
            models.Index(fields=['generated_by']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.report_type})"


class KPI(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    metric_type = models.CharField(max_length=20, choices=[
        ('COUNT', 'Count'),
        ('PERCENTAGE', 'Percentage'),
        ('AVERAGE', 'Average'),
        ('RATIO', 'Ratio'),
    ])
    target_value = models.DecimalField(max_digits=10, decimal_places=2)
    current_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit = models.CharField(max_length=20, blank=True)
    academic_year = models.CharField(max_length=9)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'KPI'
        verbose_name_plural = 'KPIs'
    
    def __str__(self):
        return f"{self.name} ({self.current_value}/{self.target_value})"
    
    @property
    def achievement_percentage(self):
        if self.target_value > 0:
            return (self.current_value / self.target_value) * 100
        return 0
