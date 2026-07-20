from django.db import models
from django.conf import settings


class IncidentType(models.TextChoices):
    LATE_COMING = 'LATE_COMING', 'Late Coming'
    ABSENCE = 'ABSENCE', 'Absence'
    UNIFORM_VIOLATION = 'UNIFORM_VIOLATION', 'Uniform Violation'
    DISRESPECT = 'DISRESPECT', 'Disrespect'
    FIGHTING = 'FIGHTING', 'Fighting'
    BULLYING = 'BULLYING', 'Bullying'
    CHEATING = 'CHEATING', 'Cheating'
    VANDALISM = 'VANDALISM', 'Vandalism'
    THEFT = 'THEFT', 'Theft'
    SUBSTANCE_ABUSE = 'SUBSTANCE_ABUSE', 'Substance Abuse'
    OTHER = 'OTHER', 'Other'


class IncidentSeverity(models.TextChoices):
    MINOR = 'MINOR', 'Minor'
    MODERATE = 'MODERATE', 'Moderate'
    SERIOUS = 'SERIOUS', 'Serious'
    SEVERE = 'SEVERE', 'Severe'


class IncidentStatus(models.TextChoices):
    REPORTED = 'REPORTED', 'Reported'
    INVESTIGATING = 'INVESTIGATING', 'Investigating'
    RESOLVED = 'RESOLVED', 'Resolved'
    ESCALATED = 'ESCALATED', 'Escalated'


class DisciplinaryIncident(models.Model):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='incidents')
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reported_incidents'
    )
    incident_type = models.CharField(max_length=20, choices=IncidentType.choices)
    severity = models.CharField(max_length=20, choices=IncidentSeverity.choices)
    title = models.CharField(max_length=200)
    description = models.TextField()
    incident_date = models.DateField()
    incident_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    witnesses = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=IncidentStatus.choices, default='REPORTED')
    action_taken = models.TextField(blank=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-incident_date']
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['incident_type']),
            models.Index(fields=['severity']),
            models.Index(fields=['status']),
            models.Index(fields=['incident_date']),
        ]
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.title}"


class BehaviorPlan(models.Model):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='behavior_plans')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_behavior_plans'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    goals = models.TextField()
    strategies = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    review_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    progress_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.title}"
