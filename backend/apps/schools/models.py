from django.db import models
from django.conf import settings


class SchoolType(models.TextChoices):
    JUNIOR = 'JUNIOR', 'Junior Secondary School'
    SENIOR = 'SENIOR', 'Senior Secondary School'


class LocalGovernmentArea(models.TextChoices):
    APAPA = 'APAPA', 'Apapa'
    MAINLAND = 'MAINLAND', 'Mainland'
    SURULERE = 'SURULERE', 'Surulere'


class School(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    school_type = models.CharField(max_length=10, choices=SchoolType.choices)
    lga = models.CharField(max_length=20, choices=LocalGovernmentArea.choices)
    address = models.TextField()
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    principal = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='schools_as_principal'
    )
    vice_principal = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='schools_as_vice_principal'
    )
    established_date = models.DateField(null=True, blank=True)
    student_capacity = models.IntegerField(default=0)
    current_enrollment = models.IntegerField(default=0)
    number_of_classrooms = models.IntegerField(default=0)
    number_of_staff = models.IntegerField(default=0)
    has_science_lab = models.BooleanField(default=False)
    has_computer_lab = models.BooleanField(default=False)
    has_library = models.BooleanField(default=False)
    has_sports_field = models.BooleanField(default=False)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['lga', 'school_type', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['school_type']),
            models.Index(fields=['lga']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def occupancy_rate(self):
        if self.student_capacity > 0:
            return (self.current_enrollment / self.student_capacity) * 100
        return 0


class SchoolAcademicYear(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='academic_years')
    year = models.CharField(max_length=9)  # e.g., "2024/2025"
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['school', 'year']
        ordering = ['-year']
    
    def __str__(self):
        return f"{self.school.name} - {self.year}"
