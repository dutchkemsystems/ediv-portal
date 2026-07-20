from django.db import models
from django.conf import settings


class MessageType(models.TextChoices):
    INTERNAL = 'INTERNAL', 'Internal Message'
    CIRCULAR = 'CIRCULAR', 'Circular'
    ANNOUNCEMENT = 'ANNOUNCEMENT', 'Announcement'
    ALERT = 'ALERT', 'Alert'
    REMINDER = 'REMINDER', 'Reminder'


class MessagePriority(models.TextChoices):
    LOW = 'LOW', 'Low'
    NORMAL = 'NORMAL', 'Normal'
    HIGH = 'HIGH', 'High'
    URGENT = 'URGENT', 'Urgent'


class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    subject = models.CharField(max_length=200)
    body = models.TextField()
    message_type = models.CharField(max_length=20, choices=MessageType.choices)
    priority = models.CharField(max_length=20, choices=MessagePriority.choices, default='NORMAL')
    recipients = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='received_messages')
    cc = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='cc_messages')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    attachment = models.FileField(upload_to='messages/attachments/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sender']),
            models.Index(fields=['message_type']),
            models.Index(fields=['priority']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.subject} - {self.sender.get_full_name()}"


class NotificationType(models.TextChoices):
    INFO = 'INFO', 'Information'
    SUCCESS = 'SUCCESS', 'Success'
    WARNING = 'WARNING', 'Warning'
    ERROR = 'ERROR', 'Error'


class UserNotification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices, default='INFO')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    link = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['is_read']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.get_full_name()}"


class Circular(models.Model):
    title = models.CharField(max_length=200)
    reference_number = models.CharField(max_length=50, unique=True)
    content = models.TextField()
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='issued_circulars'
    )
    target_audience = models.JSONField(default=list)
    priority = models.CharField(max_length=20, choices=MessagePriority.choices, default='NORMAL')
    effective_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    attachment = models.FileField(upload_to='circulars/attachments/', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-effective_date']
        indexes = [
            models.Index(fields=['reference_number']),
            models.Index(fields=['effective_date']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.reference_number} - {self.title}"
