from django.db import models
from django.conf import settings


class CounselingType(models.TextChoices):
    ACADEMIC = 'ACADEMIC', 'Academic'
    BEHAVIORAL = 'BEHAVIORAL', 'Behavioral'
    EMOTIONAL = 'EMOTIONAL', 'Emotional'
    SOCIAL = 'SOCIAL', 'Social'
    CAREER = 'CAREER', 'Career'
    PERSONAL = 'PERSONAL', 'Personal'


class CounselingSession(models.Model):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='counseling_sessions')
    counselor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='counseling_sessions'
    )
    counseling_type = models.CharField(max_length=20, choices=CounselingType.choices)
    session_date = models.DateField()
    session_time = models.TimeField()
    duration_minutes = models.IntegerField(default=60)
    notes = models.TextField()
    recommendations = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    is_confidential = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-session_date']
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['counselor']),
            models.Index(fields=['session_date']),
        ]
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.counseling_type} ({self.session_date})"


class WellnessCheckIn(models.Model):
    class MoodChoice(models.TextChoices):
        GREAT = 'GREAT', 'Great'
        GOOD = 'GOOD', 'Good'
        OKAY = 'OKAY', 'Okay'
        SAD = 'SAD', 'Sad'
        ANXIOUS = 'ANXIOUS', 'Anxious'
        ANGRY = 'ANGRY', 'Angry'
    
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='wellness_checkins')
    date = models.DateField()
    mood = models.CharField(max_length=20, choices=MoodChoice.choices)
    stress_level = models.IntegerField(default=5)
    sleep_hours = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    exercise_minutes = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    concerns = models.TextField(blank=True)
    is_flagged = models.BooleanField(default=False)
    flagged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='flagged_checkins'
    )
    flag_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['date']),
            models.Index(fields=['mood']),
            models.Index(fields=['is_flagged']),
        ]
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.mood} ({self.date})"


class WellnessResource(models.Model):
    class ResourceType(models.TextChoices):
        ARTICLE = 'ARTICLE', 'Article'
        VIDEO = 'VIDEO', 'Video'
        CONTACT = 'CONTACT', 'Contact'
    name = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=20, choices=ResourceType.choices)
    description = models.TextField()
    url = models.URLField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True)
    is_emergency = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
