from django.db import models
from django.conf import settings
from apps.schools.models import School


class StudentStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    INACTIVE = 'INACTIVE', 'Inactive'
    GRADUATED = 'GRADUATED', 'Graduated'
    TRANSFERRED = 'TRANSFERRED', 'Transferred'
    EXPELLED = 'EXPELLED', 'Expelled'
    WITHDRAWN = 'WITHDRAWN', 'Withdrawn'


class Student(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    admission_number = models.CharField(max_length=20, unique=True)
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='students'
    )
    class_name = models.ForeignKey(
        'academics.Class',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students'
    )
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')])
    blood_group = models.CharField(max_length=5, blank=True)
    nationality = models.CharField(max_length=50, default='Nigerian')
    state_of_origin = models.CharField(max_length=50)
    lga_of_origin = models.CharField(max_length=50)
    residential_address = models.TextField()
    parent_name = models.CharField(max_length=200)
    parent_phone = models.CharField(max_length=20)
    parent_email = models.EmailField(blank=True)
    parent_occupation = models.CharField(max_length=100, blank=True)
    parent_address = models.TextField(blank=True)
    guardian_name = models.CharField(max_length=200, blank=True)
    guardian_phone = models.CharField(max_length=20, blank=True)
    medical_conditions = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=200)
    emergency_contact_phone = models.CharField(max_length=20)
    previous_school = models.CharField(max_length=200, blank=True)
    admission_date = models.DateField()
    status = models.CharField(max_length=20, choices=StudentStatus.choices, default='ACTIVE')
    profile_photo = models.FileField(upload_to='students/photos/', blank=True)
    is_boarding = models.BooleanField(default=False)
    bus_route = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['admission_number']
        indexes = [
            models.Index(fields=['admission_number']),
            models.Index(fields=['school']),
            models.Index(fields=['status']),
            models.Index(fields=['gender']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.admission_number})"
    
    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )


class StudentParentRelation(models.TextChoices):
    FATHER = 'FATHER', 'Father'
    MOTHER = 'MOTHER', 'Mother'
    GUARDIAN = 'GUARDIAN', 'Guardian'
    UNCLE = 'UNCLE', 'Uncle'
    AUNT = 'AUNT', 'Aunt'
    SIBLING = 'SIBLING', 'Sibling'
    OTHER = 'OTHER', 'Other'


class StudentParent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='parents')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='children'
    )
    relation = models.CharField(max_length=20, choices=StudentParentRelation.choices)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'user']
        ordering = ['-is_primary']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.user.get_full_name()} ({self.relation})"


class StudentMedicalRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='medical_records')
    record_date = models.DateField()
    condition = models.CharField(max_length=200)
    description = models.TextField()
    treatment = models.TextField(blank=True)
    medication = models.TextField(blank=True)
    doctor_name = models.CharField(max_length=200, blank=True)
    hospital = models.CharField(max_length=200, blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-record_date']
        verbose_name_plural = 'student medical records'
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.condition}"
