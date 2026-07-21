from rest_framework import serializers
from .models import NotificationTemplate, NotificationLog


class NotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = ['id', 'name', 'subject', 'body', 'channel', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationLogSerializer(serializers.ModelSerializer):
    recipient_name = serializers.SerializerMethodField()
    
    class Meta:
        model = NotificationLog
        fields = ['id', 'template', 'recipient', 'recipient_name', 'channel', 'subject',
                  'body', 'is_sent', 'sent_at', 'error_message', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_recipient_name(self, obj):
        return obj.recipient.get_full_name()

