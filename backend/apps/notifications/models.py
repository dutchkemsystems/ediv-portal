from django.db import models
from django.conf import settings


class NotificationChannel(models.TextChoices):
    IN_APP = 'IN_APP', 'In-App'
    EMAIL = 'EMAIL', 'Email'
    SMS = 'SMS', 'SMS'
    PUSH = 'PUSH', 'Push Notification'


class NotificationTemplate(models.Model):
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    channel = models.CharField(max_length=20, choices=NotificationChannel.choices)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.channel})"


class NotificationLog(models.Model):
    template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE, related_name='logs')
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_logs'
    )
    channel = models.CharField(max_length=20, choices=NotificationChannel.choices)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient']),
            models.Index(fields=['channel']),
            models.Index(fields=['is_sent']),
        ]
    
    def __str__(self):
        return f"{self.subject} to {self.recipient.get_full_name()}"
