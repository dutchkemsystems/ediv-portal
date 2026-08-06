from rest_framework import serializers
from .models import DeviceToken, PushNotification, NotificationLog


class DeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceToken
        fields = ['id', 'token', 'platform', 'device_name', 'is_active', 'last_used', 'created_at']
        read_only_fields = ['id', 'last_used', 'created_at']


class PushNotificationSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = PushNotification
        fields = ['id', 'title', 'message', 'category', 'target_users', 'target_roles',
                  'target_schools', 'data', 'image_url', 'action_url',
                  'sent_at', 'sent_count', 'delivered_count', 'opened_count',
                  'created_by', 'created_by_name', 'created_at']
        read_only_fields = ['id', 'sent_at', 'sent_count', 'delivered_count',
                           'opened_count', 'created_at']

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else None


class NotificationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationLog
        fields = ['id', 'notification', 'device_token', 'status', 'error_message', 'created_at']
        read_only_fields = ['id', 'created_at']


class SendNotificationSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    message = serializers.CharField()
    category = serializers.ChoiceField(choices=PushNotification.CATEGORY_CHOICES, default='GENERAL')
    user_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    roles = serializers.ListField(child=serializers.CharField(), required=False)
    school_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    data = serializers.DictField(required=False, default=dict)
