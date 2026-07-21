from django.db import models
from django.conf import settings


class TrainingType(models.TextChoices):
    WORKSHOP = 'WORKSHOP', 'Workshop'
    SEMINAR = 'SEMINAR', 'Seminar'
    CONFERENCE = 'CONFERENCE', 'Conference'
    COURSE = 'COURSE', 'Course'
    CERTIFICATION = 'CERTIFICATION', 'Certification'
    MENTORING = 'MENTORING', 'Mentoring'
    SELF_STUDY = 'SELF_STUDY', 'Self Study'


class TrainingStatus(models.TextChoices):
    PLANNED = 'PLANNED', 'Planned'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    COMPLETED = 'COMPLETED', 'Completed'
    CANCELLED = 'CANCELLED', 'Cancelled'


class CPDActivity(models.Model):
    title = models.CharField(max_length=200)
    training_type = models.CharField(max_length=20, choices=TrainingType.choices)
    description = models.TextField()
    provider = models.CharField(max_length=200)
    venue = models.CharField(max_length=200, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    duration_hours = models.DecimalField(max_digits=6, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_participants = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=TrainingStatus.choices, default='PLANNED')
    is_mandatory = models.BooleanField(default=False)
    certificate_available = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['training_type']),
            models.Index(fields=['status']),
            models.Index(fields=['start_date']),
        ]
    
    def __str__(self):
        return self.title


class CPDEnrollment(models.Model):
    activity = models.ForeignKey(CPDActivity, on_delete=models.CASCADE, related_name='enrollments')
    staff = models.ForeignKey('staff.Staff', on_delete=models.CASCADE, related_name='cpd_enrollments')
    enrollment_date = models.DateField()
    completion_date = models.DateField(null=True, blank=True)
    certificate = models.FileField(upload_to='cpd/certificates/', blank=True)
    hours_completed = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    feedback = models.TextField(blank=True)
    rating = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['activity', 'staff']
        ordering = ['-enrollment_date']
    
    def __str__(self):
        return f"{self.staff.user.get_full_name()} - {self.activity.title}"


class CPDRecord(models.Model):
    staff = models.ForeignKey('staff.Staff', on_delete=models.CASCADE, related_name='cpd_records')
    academic_year = models.CharField(max_length=9)
    total_hours_required = models.DecimalField(max_digits=6, decimal_places=2, default=40)
    total_hours_completed = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    activities_completed = models.IntegerField(default=0)
    certificates_earned = models.IntegerField(default=0)
    is_compliant = models.BooleanField(default=False)
    last_review_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['staff', 'academic_year']
        ordering = ['-academic_year']
    
    def __str__(self):
        return f"{self.staff.user.get_full_name()} - {self.academic_year}"
    
    @property
    def completion_percentage(self):
        if self.total_hours_required > 0:
            return (self.total_hours_completed / self.total_hours_required) * 100
        return 0
