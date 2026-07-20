from django.db import models
from django.conf import settings
from apps.schools.models import School


class FacilityType(models.TextChoices):
    CLASSROOM = 'CLASSROOM', 'Classroom'
    LABORATORY = 'LABORATORY', 'Laboratory'
    LIBRARY = 'LIBRARY', 'Library'
    COMPUTER_LAB = 'COMPUTER_LAB', 'Computer Lab'
    SPORTS_FIELD = 'SPORTS_FIELD', 'Sports Field'
    PLAYGROUND = 'PLAYGROUND', 'Playground'
    OFFICE = 'OFFICE', 'Office'
    STORE = 'STORE', 'Store'
    TOILET = 'TOILET', 'Toilet'
    KITCHEN = 'KITCHEN', 'Kitchen'
    HALL = 'HALL', 'Hall'
    OTHER = 'OTHER', 'Other'


class FacilityCondition(models.TextChoices):
    EXCELLENT = 'EXCELLENT', 'Excellent'
    GOOD = 'GOOD', 'Good'
    FAIR = 'FAIR', 'Fair'
    POOR = 'POOR', 'Poor'
    CRITICAL = 'CRITICAL', 'Critical'


class Facility(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='facilities')
    name = models.CharField(max_length=200)
    facility_type = models.CharField(max_length=20, choices=FacilityType.choices)
    description = models.TextField(blank=True)
    condition = models.CharField(max_length=20, choices=FacilityCondition.choices, default='GOOD')
    capacity = models.IntegerField(default=0)
    year_built = models.IntegerField(null=True, blank=True)
    last_maintenance = models.DateField(null=True, blank=True)
    next_maintenance = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['school', 'facility_type', 'name']
        indexes = [
            models.Index(fields=['school']),
            models.Index(fields=['facility_type']),
            models.Index(fields=['condition']),
        ]
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"


class MaintenanceRequest(models.Model):
    class RequestStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        REJECTED = 'REJECTED', 'Rejected'
    
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name='maintenance_requests')
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=[
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ], default='MEDIUM')
    status = models.CharField(max_length=20, choices=RequestStatus.choices, default='PENDING')
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='maintenance_requests'
    )
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_maintenance'
    )
    completion_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['facility']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        return f"{self.facility.name} - {self.title}"


class Project(models.Model):
    class ProjectStatus(models.TextChoices):
        PLANNING = 'PLANNING', 'Planning'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        ON_HOLD = 'ON_HOLD', 'On Hold'
        CANCELLED = 'CANCELLED', 'Cancelled'
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=ProjectStatus.choices, default='PLANNING')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    project_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_projects'
    )
    progress_percentage = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['school']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"
    
    @property
    def remaining_budget(self):
        return self.budget - self.spent
