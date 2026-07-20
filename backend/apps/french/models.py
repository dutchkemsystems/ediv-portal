from django.db import models
from django.conf import settings
from apps.schools.models import School


class FrenchLevel(models.TextChoices):
    BEGINNER = 'BEGINNER', 'Beginner'
    ELEMENTARY = 'ELEMENTARY', 'Elementary'
    INTERMEDIATE = 'INTERMEDIATE', 'Intermediate'
    ADVANCED = 'ADVANCED', 'Advanced'
    FLUENT = 'FLUENT', 'Fluent'


class FrenchProgram(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    level = models.CharField(max_length=20, choices=FrenchLevel.choices)
    duration_weeks = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['level', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.level})"


class FrenchClub(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='french_clubs')
    name = models.CharField(max_length=200)
    coordinator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='coordinated_french_clubs'
    )
    meeting_schedule = models.CharField(max_length=200, blank=True)
    meeting_venue = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['school', 'name']
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"


class FrenchClubMember(models.Model):
    club = models.ForeignKey(FrenchClub, on_delete=models.CASCADE, related_name='members')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='french_club_memberships')
    role = models.CharField(max_length=100, blank=True)
    joined_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['club', 'student']
        ordering = ['club', 'student']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.club.name}"


class FrenchCompetition(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    level = models.CharField(max_length=20, choices=FrenchLevel.choices)
    venue = models.CharField(max_length=200)
    date = models.DateField()
    organizer = models.CharField(max_length=200)
    max_participants = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return self.name
