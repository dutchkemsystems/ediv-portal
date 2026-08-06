from django.db import models
from django.conf import settings


class DeviceToken(models.Model):
    PLATFORM_CHOICES = [
        ('IOS', 'iOS'),
        ('ANDROID', 'Android'),
        ('WEB', 'Web Browser'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                            related_name='device_tokens')
    token = models.CharField(max_length=500, unique=True)
    platform = models.CharField(max_length=10, choices=PLATFORM_CHOICES)
    device_name = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    last_used = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'device_tokens'
        unique_together = ['user', 'token']

    def __str__(self):
        return f"{self.user.email} - {self.platform}"


class PushNotification(models.Model):
    CATEGORY_CHOICES = [
        ('RESULTS', 'Exam Results'),
        ('ATTENDANCE', 'Attendance Alert'),
        ('FEES', 'Fee Reminder'),
        ('ANNOUNCEMENT', 'School Announcement'),
        ('EMERGENCY', 'Emergency Alert'),
        ('ASSIGNMENT', 'Assignment'),
        ('EVENT', 'School Event'),
        ('GENERAL', 'General'),
    ]

    title = models.CharField(max_length=200)
    message = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='GENERAL')
    target_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True,
                                         related_name='push_notifications')
    target_roles = models.JSONField(default=list, help_text='Target specific roles')
    target_schools = models.ManyToManyField('schools.School', blank=True,
                                           related_name='push_notifications')
    data = models.JSONField(default=dict, help_text='Additional data payload')
    image_url = models.URLField(blank=True)
    action_url = models.CharField(max_length=500, blank=True)

    sent_at = models.DateTimeField(null=True, blank=True)
    sent_count = models.IntegerField(default=0)
    delivered_count = models.IntegerField(default=0)
    opened_count = models.IntegerField(default=0)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, related_name='created_notifications')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'push_notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.category})"


class NotificationLog(models.Model):
    notification = models.ForeignKey(PushNotification, on_delete=models.CASCADE,
                                    related_name='logs')
    device_token = models.ForeignKey(DeviceToken, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('OPENED', 'Opened'),
        ('FAILED', 'Failed'),
    ])
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notification_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification.title} - {self.status}"
