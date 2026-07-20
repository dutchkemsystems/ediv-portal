from django.db import models
from django.conf import settings
from apps.schools.models import School


class InspectionStatus(models.TextChoices):
    SCHEDULED = 'SCHEDULED', 'Scheduled'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    COMPLETED = 'COMPLETED', 'Completed'
    CANCELLED = 'CANCELLED', 'Cancelled'


class InspectionType(models.TextChoices):
    ROUTINE = 'ROUTINE', 'Routine Inspection'
    SURPRISE = 'SURPRISE', 'Surprise Inspection'
    FOLLOW_UP = 'FOLLOW_UP', 'Follow-up Inspection'
    SPECIAL = 'SPECIAL', 'Special Inspection'


class Inspection(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='inspections')
    title = models.CharField(max_length=200)
    inspection_type = models.CharField(max_length=20, choices=InspectionType.choices)
    scheduled_date = models.DateField()
    actual_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=InspectionStatus.choices, default='SCHEDULED')
    lead_inspector = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='led_inspections'
    )
    team_members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='inspection_teams')
    objectives = models.TextField()
    findings = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    overall_rating = models.CharField(max_length=20, choices=[
        ('EXCELLENT', 'Excellent'),
        ('VERY_GOOD', 'Very Good'),
        ('GOOD', 'Good'),
        ('SATISFACTORY', 'Satisfactory'),
        ('NEEDS_IMPROVEMENT', 'Needs Improvement'),
        ('UNSATISFACTORY', 'Unsatisfactory'),
    ], blank=True)
    report_file = models.FileField(upload_to='inspections/reports/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_date']
        indexes = [
            models.Index(fields=['school']),
            models.Index(fields=['inspection_type']),
            models.Index(fields=['status']),
            models.Index(fields=['scheduled_date']),
        ]
    
    def __str__(self):
        return f"{self.school.name} - {self.title}"


class InspectionChecklist(models.Model):
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE, related_name='checklists')
    category = models.CharField(max_length=100)
    item = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_mandatory = models.BooleanField(default=True)
    rating = models.CharField(max_length=20, choices=[
        ('EXCELLENT', 'Excellent'),
        ('GOOD', 'Good'),
        ('SATISFACTORY', 'Satisfactory'),
        ('POOR', 'Poor'),
        ('NOT_APPLICABLE', 'Not Applicable'),
    ], blank=True)
    remarks = models.TextField(blank=True)
    evidence_file = models.FileField(upload_to='inspections/evidence/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'item']
        verbose_name_plural = 'inspection checklists'
    
    def __str__(self):
        return f"{self.inspection.title} - {self.category}: {self.item}"


class InspectionAction(models.Model):
    class ActionStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        OVERDUE = 'OVERDUE', 'Overdue'
    
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE, related_name='actions')
    action = models.CharField(max_length=200)
    description = models.TextField()
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='inspection_actions'
    )
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=ActionStatus.choices, default='PENDING')
    completion_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['due_date', 'status']
    
    def __str__(self):
        return f"{self.inspection.title} - {self.action}"
