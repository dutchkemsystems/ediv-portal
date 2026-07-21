from django.db import models
from django.conf import settings


class ReportType(models.TextChoices):
    ACADEMIC = 'ACADEMIC', 'Academic Report'
    FINANCIAL = 'FINANCIAL', 'Financial Report'
    ATTENDANCE = 'ATTENDANCE', 'Attendance Report'
    STAFF = 'STAFF', 'Staff Report'
    INSPECTION = 'INSPECTION', 'Inspection Report'
    ENROLLMENT = 'ENROLLMENT', 'Enrollment Report'
    PERFORMANCE = 'PERFORMANCE', 'Performance Report'
    CUSTOM = 'CUSTOM', 'Custom Report'


class Report(models.Model):
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=ReportType.choices)
    description = models.TextField(blank=True)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='generated_reports'
    )
    parameters = models.JSONField(default=dict)
    file = models.FileField(upload_to='reports/', blank=True)
    is_scheduled = models.BooleanField(default=False)
    schedule_cron = models.CharField(max_length=50, blank=True)
    last_generated = models.DateTimeField(null=True, blank=True)
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


class DashboardWidget(models.TextChoices):
    STAT_CARD = 'STAT_CARD', 'Statistic Card'
    LINE_CHART = 'LINE_CHART', 'Line Chart'
    BAR_CHART = 'BAR_CHART', 'Bar Chart'
    PIE_CHART = 'PIE_CHART', 'Pie Chart'
    TABLE = 'TABLE', 'Data Table'
    MAP = 'MAP', 'Map'
    PROGRESS = 'PROGRESS', 'Progress Bar'


class Dashboard(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dashboards'
    )
    is_default = models.BooleanField(default=False)
    layout = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['is_default']),
        ]
    
    def __str__(self):
        return self.name


class Widget(models.Model):
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='widgets')
    title = models.CharField(max_length=200)
    widget_type = models.CharField(max_length=20, choices=DashboardWidget.choices)
    data_source = models.CharField(max_length=200)
    config = models.JSONField(default=dict)
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    width = models.IntegerField(default=6)
    height = models.IntegerField(default=4)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['position_y', 'position_x']
        verbose_name_plural = 'widgets'
    
    def __str__(self):
        return f"{self.dashboard.name} - {self.title}"
