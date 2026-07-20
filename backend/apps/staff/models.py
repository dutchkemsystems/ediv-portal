from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.schools.models import School


class StaffCategory(models.TextChoices):
    TEACHING = 'TEACHING', 'Teaching Staff'
    NON_TEACHING = 'NON_TEACHING', 'Non-Teaching Staff'
    ADMINISTRATIVE = 'ADMINISTRATIVE', 'Administrative Staff'


class StaffDesignation(models.TextChoices):
    PRINCIPAL = 'PRINCIPAL', 'Principal'
    VICE_PRINCIPAL = 'VICE_PRINCIPAL', 'Vice Principal'
    HEAD_TEACHER = 'HEAD_TEACHER', 'Head Teacher'
    SENIOR_TEACHER = 'SENIOR_TEACHER', 'Senior Teacher'
    TEACHER = 'TEACHER', 'Teacher'
    LIBRARIAN = 'LIBRARIAN', 'Librarian'
    LABORATORY_ATTENDANT = 'LABORATORY_ATTENDANT', 'Laboratory Attendant'
    BURSAR = 'BURSAR', 'Bursar'
    SECRETARY = 'SECRETARY', 'Secretary'
    CLERK = 'CLERK', 'Clerk'
    GARDENER = 'GARDENER', 'Gardener'
    SECURITY = 'SECURITY', 'Security'
    CLEANER = 'CLEANER', 'Cleaner'
    DRIVER = 'DRIVER', 'Driver'
    TECHNICIAN = 'TECHNICIAN', 'Technician'


class StaffEmploymentType(models.TextChoices):
    PERMANENT = 'PERMANENT', 'Permanent'
    CONTRACT = 'CONTRACT', 'Contract'
    TEMPORARY = 'TEMPORARY', 'Temporary'
    VOLUNTEER = 'VOLUNTEER', 'Volunteer'


class StaffQualification(models.TextChoices):
    PhD = 'PhD', 'Doctorate'
    MASTERS = 'Masters', 'Masters Degree'
    BACHELORS = 'Bachelors', 'Bachelors Degree'
    HND = 'HND', 'Higher National Diploma'
    OND = 'OND', 'Ordinary National Diploma'
    NCE = 'NCE', 'Nigeria Certificate in Education'
    SSCE = 'SSCE', 'Senior School Certificate'
    OTHER = 'OTHER', 'Other'


class Staff(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='staff_profile'
    )
    staff_id = models.CharField(max_length=20, unique=True)
    employee_number = models.CharField(max_length=20, unique=True)
    school = models.ForeignKey(
        School,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff'
    )
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff_members'
    )
    category = models.CharField(max_length=20, choices=StaffCategory.choices)
    designation = models.CharField(max_length=20, choices=StaffDesignation.choices)
    employment_type = models.CharField(max_length=20, choices=StaffEmploymentType.choices)
    qualification = models.CharField(max_length=20, choices=StaffQualification.choices)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')])
    marital_status = models.CharField(max_length=20, choices=[
        ('SINGLE', 'Single'),
        ('MARRIED', 'Married'),
        ('DIVORCED', 'Divorced'),
        ('WIDOWED', 'Widowed'),
    ])
    state_of_origin = models.CharField(max_length=50)
    lga_of_origin = models.CharField(max_length=50)
    residential_address = models.TextField()
    emergency_contact_name = models.CharField(max_length=200)
    emergency_contact_phone = models.CharField(max_length=20)
    bank_name = models.CharField(max_length=100)
    bank_account_number = models.CharField(max_length=20)
    bank_account_name = models.CharField(max_length=200)
    pension_pin = models.CharField(max_length=20, blank=True)
    tax_id = models.CharField(max_length=20, blank=True)
    date_joined = models.DateField()
    date_of_first_appointment = models.DateField(null=True, blank=True)
    date_of_retirement = models.DateField(null=True, blank=True)
    grade_level = models.CharField(max_length=20, blank=True)
    step = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(17)])
    salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    is_suspended = models.BooleanField(default=False)
    suspension_reason = models.TextField(blank=True)
    profile_photo = models.FileField(upload_to='staff/photos/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['staff_id']
        indexes = [
            models.Index(fields=['staff_id']),
            models.Index(fields=['employee_number']),
            models.Index(fields=['category']),
            models.Index(fields=['designation']),
            models.Index(fields=['school']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.staff_id})"
    
    @property
    def years_of_service(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_joined.year - (
            (today.month, today.day) < (self.date_joined.month, self.date_joined.day)
        )


class StaffLeave(models.Model):
    class LeaveType(models.TextChoices):
        ANNUAL = 'ANNUAL', 'Annual Leave'
        SICK = 'SICK', 'Sick Leave'
        MATERNITY = 'MATERNITY', 'Maternity Leave'
        PATERNITY = 'PATERNITY', 'Paternity Leave'
        COMPASSIONATE = 'COMPASSIONATE', 'Compassionate Leave'
        STUDY = 'STUDY', 'Study Leave'
        EDUCATIONAL = 'EDUCATIONAL', 'Educational Leave'
        EXAMINATION = 'EXAMINATION', 'Examination Leave'
        CASUAL = 'CASUAL', 'Casual Leave'
    
    class LeaveStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        CANCELLED = 'CANCELLED', 'Cancelled'
    
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.CharField(max_length=20, choices=LeaveType.choices)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=LeaveStatus.choices, default='PENDING')
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leaves'
    )
    approval_date = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['leave_type']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.staff.user.get_full_name()} - {self.leave_type}"
    
    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days + 1


class StaffPerformance(models.Model):
    class PerformanceRating(models.TextChoices):
        EXCELLENT = 'EXCELLENT', 'Excellent'
        VERY_GOOD = 'VERY_GOOD', 'Very Good'
        GOOD = 'GOOD', 'Good'
        SATISFACTORY = 'SATISFACTORY', 'Satisfactory'
        NEEDS_IMPROVEMENT = 'NEEDS_IMPROVEMENT', 'Needs Improvement'
        UNSATISFACTORY = 'UNSATISFACTORY', 'Unsatisfactory'
    
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='performances')
    academic_year = models.CharField(max_length=9)
    term = models.CharField(max_length=20, choices=[
        ('FIRST', 'First Term'),
        ('SECOND', 'Second Term'),
        ('THIRD', 'Third Term'),
    ])
    rating = models.CharField(max_length=20, choices=PerformanceRating.choices)
    punctuality_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    dedication_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    teaching_quality_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    student_performance_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    comments = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='performance_reviews'
    )
    review_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['staff', 'academic_year', 'term']
        ordering = ['-academic_year', '-term']
        indexes = [
            models.Index(fields=['academic_year']),
            models.Index(fields=['rating']),
        ]
    
    def __str__(self):
        return f"{self.staff.user.get_full_name()} - {self.academic_year} {self.term}"
    
    @property
    def average_score(self):
        scores = [
            self.punctuality_score,
            self.dedication_score,
            self.teaching_quality_score,
            self.student_performance_score,
        ]
        return sum(scores) / len(scores)
