from django.db import models
from django.conf import settings
from apps.schools.models import School


class ClassLevel(models.TextChoices):
    JSS1 = 'JSS1', 'Junior Secondary School 1'
    JSS2 = 'JSS2', 'Junior Secondary School 2'
    JSS3 = 'JSS3', 'Junior Secondary School 3'
    SS1 = 'SS1', 'Senior Secondary School 1'
    SS2 = 'SS2', 'Senior Secondary School 2'
    SS3 = 'SS3', 'Senior Secondary School 3'


class Class(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='classes')
    name = models.CharField(max_length=100)
    level = models.CharField(max_length=10, choices=ClassLevel.choices)
    section = models.CharField(max_length=10, blank=True)
    capacity = models.IntegerField(default=40)
    class_teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='class_teacher_of'
    )
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
        ordering = ['school', 'level', 'section']
        unique_together = ['school', 'name', 'academic_year', 'term']
        indexes = [
            models.Index(fields=['school']),
            models.Index(fields=['level']),
            models.Index(fields=['academic_year']),
        ]
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"
    
    @property
    def current_enrollment(self):
        return self.students.count()


class Subject(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=[
        ('SCIENCE', 'Science'),
        ('ARTS', 'Arts'),
        ('COMMERCIAL', 'Commercial'),
        ('TECHNICAL', 'Technical'),
        ('GENERAL', 'General'),
    ])
    is_compulsory = models.BooleanField(default=False)
    applicable_levels = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class ClassSubject(models.Model):
    class Meta:
        unique_together = ['class_obj', 'subject']
        verbose_name_plural = 'class subjects'
    
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='class_subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='class_subjects')
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teaching_subjects'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.class_obj.name} - {self.subject.name}"


class ExamType(models.TextChoices):
    CA1 = 'CA1', 'Continuous Assessment 1'
    CA2 = 'CA2', 'Continuous Assessment 2'
    CA3 = 'CA3', 'Continuous Assessment 3'
    MIDTERM = 'MIDTERM', 'Mid-Term Exam'
    FINAL = 'FINAL', 'Final Exam'


class Exam(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='exams')
    name = models.CharField(max_length=200)
    exam_type = models.CharField(max_length=20, choices=ExamType.choices)
    academic_year = models.CharField(max_length=9)
    term = models.CharField(max_length=20, choices=[
        ('FIRST', 'First Term'),
        ('SECOND', 'Second Term'),
        ('THIRD', 'Third Term'),
    ])
    start_date = models.DateField()
    end_date = models.DateField()
    total_marks = models.IntegerField(default=100)
    pass_marks = models.IntegerField(default=40)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-academic_year', '-term', 'start_date']
        indexes = [
            models.Index(fields=['school']),
            models.Index(fields=['exam_type']),
            models.Index(fields=['academic_year']),
        ]
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"


class ExamResult(models.Model):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='exam_results')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exam_results')
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=5)
    remark = models.CharField(max_length=100, blank=True)
    entered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='entered_results'
    )
    entered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'exam', 'subject']
        ordering = ['student', 'subject']
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['exam']),
            models.Index(fields=['subject']),
        ]
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.subject.name} ({self.marks_obtained})"
    
    @property
    def percentage(self):
        if self.exam.total_marks > 0:
            return (self.marks_obtained / self.exam.total_marks) * 100
        return 0


class ReportCard(models.Model):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='report_cards')
    academic_year = models.CharField(max_length=9)
    term = models.CharField(max_length=20, choices=[
        ('FIRST', 'First Term'),
        ('SECOND', 'Second Term'),
        ('THIRD', 'Third Term'),
    ])
    total_marks = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    average_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    class_position = models.IntegerField(null=True, blank=True)
    total_students = models.IntegerField(null=True, blank=True)
    teacher_remark = models.TextField(blank=True)
    principal_remark = models.TextField(blank=True)
    next_term_begins = models.DateField(null=True, blank=True)
    is_released = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'academic_year', 'term']
        ordering = ['-academic_year', '-term']
        verbose_name_plural = 'report cards'
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.academic_year} {self.term}"
    
    @property
    def position_suffix(self):
        if self.class_position is None:
            return ''
        if 11 <= self.class_position % 100 <= 13:
            suffix = 'th'
        else:
            suffix = {1: 'st', '2': 'nd', '3': 'rd'}.get(self.class_position % 10, 'th')
        return f"{self.class_position}{suffix}"


class AcademicCalendar(models.Model):
    class EventType(models.TextChoices):
        TERM_START = 'TERM_START', 'Term Start'
        TERM_END = 'TERM_END', 'Term End'
        MIDTERM = 'MIDTERM', 'Mid-Term Break'
        HOLIDAY = 'HOLIDAY', 'Holiday'
        EXAM_PERIOD = 'EXAM_PERIOD', 'Examination Period'
        RESULT_RELEASE = 'RESULT_RELEASE', 'Result Release'
        PARENT_TEACHER = 'PARENT_TEACHER', 'Parent-Teacher Meeting'
        SCHOOL_EVENT = 'SCHOOL_EVENT', 'School Event'
        OTHER = 'OTHER', 'Other'
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='academic_calendar')
    title = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=EventType.choices)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_recurring = models.BooleanField(default=False)
    academic_year = models.CharField(max_length=9)
    term = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_date']
        indexes = [
            models.Index(fields=['school']),
            models.Index(fields=['event_type']),
            models.Index(fields=['academic_year']),
            models.Index(fields=['start_date']),
        ]
    
    def __str__(self):
        return f"{self.school.name} - {self.title}"


class StudentEnrollment(models.Model):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='enrollments')
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='student_enrollments')
    academic_year = models.CharField(max_length=9)
    term = models.CharField(max_length=20, choices=[
        ('FIRST', 'First Term'),
        ('SECOND', 'Second Term'),
        ('THIRD', 'Third Term'),
    ])
    enrollment_date = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ('ACTIVE', 'Active'),
        ('TRANSFERRED', 'Transferred'),
        ('WITHDRAWN', 'Withdrawn'),
        ('GRADUATED', 'Graduated'),
    ], default='ACTIVE')
    previous_class = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'class_obj', 'academic_year', 'term']
        ordering = ['-academic_year', '-term']
        verbose_name_plural = 'student enrollments'
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.class_obj.name}"
