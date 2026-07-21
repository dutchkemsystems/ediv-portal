from django.db import models
from django.conf import settings
from django.utils import timezone


class AttendanceStatus(models.TextChoices):
    PRESENT = 'PRESENT', 'Present'
    ABSENT = 'ABSENT', 'Absent'
    LATE = 'LATE', 'Late'
    EXCUSED = 'EXCUSED', 'Excused'
    ON_LEAVE = 'ON_LEAVE', 'On Leave'


class StudentAttendance(models.Model):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=20, choices=AttendanceStatus.choices)
    time_in = models.TimeField(null=True, blank=True)
    time_out = models.TimeField(null=True, blank=True)
    remark = models.CharField(max_length=200, blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='student_attendance_records'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'date']
        ordering = ['-date', 'student']
        verbose_name_plural = 'student attendances'
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.date} ({self.status})"


class StaffAttendance(models.Model):
    staff = models.ForeignKey('staff.Staff', on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=20, choices=AttendanceStatus.choices)
    time_in = models.TimeField(null=True, blank=True)
    time_out = models.TimeField(null=True, blank=True)
    overtime_hours = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    remark = models.CharField(max_length=200, blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='staff_attendance_records'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['staff', 'date']
        ordering = ['-date', 'staff']
        verbose_name_plural = 'staff attendances'
        indexes = [
            models.Index(fields=['staff']),
            models.Index(fields=['date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.staff.user.get_full_name()} - {self.date} ({self.status})"


class AttendanceSummary(models.Model):
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='attendance_summaries')
    academic_year = models.CharField(max_length=9)
    term = models.CharField(max_length=20, choices=[
        ('FIRST', 'First Term'),
        ('SECOND', 'Second Term'),
        ('THIRD', 'Third Term'),
    ])
    total_school_days = models.IntegerField(default=0)
    total_present = models.IntegerField(default=0)
    total_absent = models.IntegerField(default=0)
    total_late = models.IntegerField(default=0)
    attendance_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['school', 'academic_year', 'term']
        ordering = ['-academic_year', '-term']
        verbose_name_plural = 'attendance summaries'
    
    def __str__(self):
        return f"{self.school.name} - {self.academic_year} {self.term}"
    
    def calculate_rate(self):
        if self.total_school_days > 0:
            self.attendance_rate = (self.total_present / (self.total_school_days * self.school.current_enrollment)) * 100
            self.save()
