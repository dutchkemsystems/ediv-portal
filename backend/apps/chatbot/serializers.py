from rest_framework import serializers
from .models import ChatSession, ChatMessage, ChatIntent


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'intent', 'confidence', 'created_at']
        read_only_fields = ['id', 'created_at']


class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatSession
        fields = ['id', 'messages', 'message_count', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_message_count(self, obj):
        return obj.messages.count()


class ChatIntentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatIntent
        fields = ['id', 'name', 'patterns', 'response_template', 'requires_auth', 'min_role', 'is_active']
        read_only_fields = ['id']


class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=2000)
    session_id = serializers.IntegerField(required=False, allow_null=True)


class ChatResponseSerializer(serializers.Serializer):
    reply = serializers.CharField()
    intent = serializers.CharField()
    confidence = serializers.FloatField()
    session_id = serializers.IntegerField()
    suggestions = serializers.ListField(child=serializers.CharField(), default=list)
