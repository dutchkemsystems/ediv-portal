from django.db import models
from django.conf import settings
from apps.schools.models import School


class AlumniMember(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='alumni_profile'
    )
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='alumni')
    graduation_year = models.IntegerField()
    class_name = models.CharField(max_length=100, blank=True)
    current_occupation = models.CharField(max_length=200, blank=True)
    company = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True)
    achievements = models.TextField(blank=True)
    is_active_alumni = models.BooleanField(default=True)
    is_donor = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-graduation_year']
        indexes = [
            models.Index(fields=['school']),
            models.Index(fields=['graduation_year']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.graduation_year})"


class AlumniEvent(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    event_date = models.DateField()
    venue = models.CharField(max_length=200)
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organized_alumni_events'
    )
    max_attendees = models.IntegerField(default=0)
    registration_deadline = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-event_date']
    
    def __str__(self):
        return self.name


class AlumniDonation(models.Model):
    donor = models.ForeignKey(AlumniMember, on_delete=models.CASCADE, related_name='donations')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    purpose = models.CharField(max_length=200)
    donation_date = models.DateField()
    receipt_number = models.CharField(max_length=50, unique=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-donation_date']
    
    def __str__(self):
        return f"{self.donor.user.get_full_name()} - {self.amount}"
