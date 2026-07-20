from django.db import models
from django.conf import settings
from apps.schools.models import School


class DayOfWeek(models.TextChoices):
    MONDAY = 'MONDAY', 'Monday'
    TUESDAY = 'TUESDAY', 'Tuesday'
    WEDNESDAY = 'WEDNESDAY', 'Wednesday'
    THURSDAY = 'THURSDAY', 'Thursday'
    FRIDAY = 'FRIDAY', 'Friday'
    SATURDAY = 'SATURDAY', 'Saturday'


class Period(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='periods')
    name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    period_number = models.IntegerField()
    is_break = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['school', 'period_number']
        unique_together = ['school', 'period_number']
    
    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"


class Timetable(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='timetables')
    class_obj = models.ForeignKey('academics.Class', on_delete=models.CASCADE, related_name='timetables')
    academic_year = models.CharField(max_length=9)
    term = models.CharField(max_length=20, choices=[
        ('FIRST', 'First Term'),
        ('SECOND', 'Second Term'),
        ('THIRD', 'Third Term'),
    ])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['school', 'class_obj', 'academic_year', 'term']
        ordering = ['school', 'academic_year']
    
    def __str__(self):
        return f"{self.class_obj.name} - {self.academic_year} {self.term}"


class TimetableEntry(models.Model):
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name='entries')
    day = models.CharField(max_length=20, choices=DayOfWeek.choices)
    period = models.ForeignKey(Period, on_delete=models.CASCADE, related_name='timetable_entries')
    subject = models.ForeignKey('academics.Subject', on_delete=models.CASCADE, related_name='timetable_entries')
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teaching_slots'
    )
    room = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['timetable', 'day', 'period']
        ordering = ['day', 'period__period_number']
    
    def __str__(self):
        return f"{self.day} - {self.period.name} - {self.subject.name}"


class TeacherTimetable(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='teacher_timetables'
    )
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name='teacher_timetables')
    
    class Meta:
        unique_together = ['teacher', 'timetable']
    
    def __str__(self):
        return f"{self.teacher.get_full_name()} - {self.timetable}"
