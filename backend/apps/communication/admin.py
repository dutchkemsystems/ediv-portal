from django.contrib import admin
from .models import Message, UserNotification, Circular


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['subject', 'sender', 'message_type', 'priority', 'is_read', 'created_at']
    list_filter = ['message_type', 'priority', 'is_read']
    search_fields = ['subject', 'body', 'sender__first_name', 'sender__last_name']
    raw_id_fields = ['sender']
    filter_horizontal = ['recipients', 'cc']


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']
    search_fields = ['title', 'message', 'user__first_name', 'user__last_name']
    raw_id_fields = ['user']


@admin.register(Circular)
class CircularAdmin(admin.ModelAdmin):
    list_display = ['reference_number', 'title', 'issued_by', 'priority', 'effective_date', 'is_active']
    list_filter = ['priority', 'is_active']
    search_fields = ['title', 'reference_number']
    raw_id_fields = ['issued_by']
