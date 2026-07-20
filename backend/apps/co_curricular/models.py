from django.db import models
from django.conf import settings
from apps.schools.models import School


class ActivityType(models.TextChoices):
    SPORTS = 'SPORTS', 'Sports'
    CLUB = 'CLUB', 'Club'
    SOCIETY = 'SOCIETY', 'Society'
    COMPETITION = 'COMPETITION', 'Competition'
    CULTURAL = 'CULTURAL', 'Cultural Activity'
    SCIENCE = 'SCIENCE', 'Science Activity'
    DEBATE = 'DEBATE', 'Debate'
    PRESS = 'PRESS', 'Press Club'
    ENVIRONMENTAL = 'ENVIRONMENTAL', 'Environmental Club'
    OTHER = 'OTHER', 'Other'


class Activity(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='activities')
    name = models.CharField(max_length=200)
    activity_type = models.CharField(max_length=20, choices=ActivityType.choices)
    description = models.TextField()
    coordinator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='coordinated_activities'
    )
    meeting_schedule = models.CharField(max_length=200, blank=True)
    meeting_venue = models.CharField(max_length=200, blank=True)
    max_participants = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['school', 'activity_type', 'name']
        indexes = [
            models.Index(fields=['school']),
            models.Index(fields=['activity_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"


class ActivityParticipant(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='participants')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='activity_participations')
    role = models.CharField(max_length=100, blank=True)
    joined_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['activity', 'student']
        ordering = ['activity', 'student']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.activity.name}"


class Competition(models.Model):
    name = models.CharField(max_length=200)
    competition_type = models.CharField(max_length=20, choices=ActivityType.choices)
    description = models.TextField()
    organizer = models.CharField(max_length=200)
    venue = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    registration_deadline = models.DateField()
    max_participants = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['competition_type']),
            models.Index(fields=['start_date']),
        ]
    
    def __str__(self):
        return self.name


class CompetitionEntry(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='entries')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='competition_entries')
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='competition_entries')
    registration_date = models.DateField()
    category = models.CharField(max_length=100, blank=True)
    position = models.IntegerField(null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    certificate = models.FileField(upload_to='competitions/certificates/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['competition', 'student']
        ordering = ['competition', 'position']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.competition.name}"
