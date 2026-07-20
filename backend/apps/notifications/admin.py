from django.contrib import admin
from .models import NotificationTemplate, NotificationLog


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'channel', 'is_active']
    list_filter = ['channel', 'is_active']
    search_fields = ['name', 'subject']


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['subject', 'recipient', 'channel', 'is_sent', 'sent_at']
    list_filter = ['channel', 'is_sent']
    search_fields = ['subject', 'recipient__first_name', 'recipient__last_name']
    raw_id_fields = ['template', 'recipient']
