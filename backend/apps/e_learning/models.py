from django.db import models
from django.conf import settings
from apps.schools.models import School


class CourseStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Draft'
    PUBLISHED = 'PUBLISHED', 'Published'
    ARCHIVED = 'ARCHIVED', 'Archived'


class Course(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='courses')
    title = models.CharField(max_length=300)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    subject = models.ForeignKey('academics.Subject', on_delete=models.CASCADE, related_name='courses')
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses_taught'
    )
    status = models.CharField(max_length=20, choices=CourseStatus.choices, default='DRAFT')
    thumbnail = models.FileField(upload_to='courses/thumbnails/', blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    max_students = models.IntegerField(default=0)
    is_certified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['school', 'title']
        indexes = [
            models.Index(fields=['school']),
            models.Index(fields=['code']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.title}"
    
    @property
    def enrolled_count(self):
        return self.enrollments.count()


class CourseModule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class LessonType(models.TextChoices):
    VIDEO = 'VIDEO', 'Video'
    DOCUMENT = 'DOCUMENT', 'Document'
    QUIZ = 'QUIZ', 'Quiz'
    ASSIGNMENT = 'ASSIGNMENT', 'Assignment'
    DISCUSSION = 'DISCUSSION', 'Discussion'


class Lesson(models.Model):
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    lesson_type = models.CharField(max_length=20, choices=LessonType.choices)
    content = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    document = models.FileField(upload_to='courses/lessons/', blank=True)
    duration_minutes = models.IntegerField(default=0)
    order = models.IntegerField(default=0)
    is_free = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.module.title} - {self.title}"


class Enrollment(models.Model):
    class EnrollmentStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        COMPLETED = 'COMPLETED', 'Completed'
        DROPPED = 'DROPPED', 'Dropped'
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='course_enrollments')
    enrollment_date = models.DateField()
    status = models.CharField(max_length=20, choices=EnrollmentStatus.choices, default='ACTIVE')
    completion_date = models.DateField(null=True, blank=True)
    certificate = models.FileField(upload_to='courses/certificates/', blank=True)
    progress_percentage = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['course', 'student']
        ordering = ['-enrollment_date']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.course.title}"


class Quiz(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    time_limit_minutes = models.IntegerField(default=30)
    passing_score = models.IntegerField(default=70)
    max_attempts = models.IntegerField(default=3)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'quizzes'
    
    def __str__(self):
        return self.title


class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField()
    question_type = models.CharField(max_length=20, choices=[
        ('MCQ', 'Multiple Choice'),
        ('TF', 'True/False'),
        ('SHORT', 'Short Answer'),
    ])
    options = models.JSONField(default=list)
    correct_answer = models.CharField(max_length=500)
    points = models.IntegerField(default=1)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.quiz.title} - Q{self.order}"


class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='quiz_attempts')
    score = models.DecimalField(max_digits=5, decimal_places=2)
    is_passed = models.BooleanField(default=False)
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    answers = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.quiz.title}"
