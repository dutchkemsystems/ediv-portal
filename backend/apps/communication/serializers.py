from rest_framework import serializers
from .models import Message, UserNotification, Circular
from apps.users.serializers import UserSerializer


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    recipient_names = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'sender_name', 'subject', 'body', 'message_type',
                  'priority', 'recipients', 'recipient_names', 'cc', 'is_read', 'read_at',
                  'attachment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_sender_name(self, obj):
        return obj.sender.get_full_name()
    
    def get_recipient_names(self, obj):
        return [user.get_full_name() for user in obj.recipients.all()]


class MessageListSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = ['id', 'sender_name', 'subject', 'message_type', 'priority', 'is_read', 'created_at']
    
    def get_sender_name(self, obj):
        return obj.sender.get_full_name()


class UserNotificationSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = UserNotification
        fields = ['id', 'user', 'user_name', 'title', 'message', 'notification_type',
                  'is_read', 'read_at', 'link', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_user_name(self, obj):
        return obj.user.get_full_name()


class CircularSerializer(serializers.ModelSerializer):
    issued_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Circular
        fields = ['id', 'title', 'reference_number', 'content', 'issued_by', 'issued_by_name',
                  'target_audience', 'priority', 'effective_date', 'expiry_date',
                  'attachment', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_issued_by_name(self, obj):
        return obj.issued_by.get_full_name()

