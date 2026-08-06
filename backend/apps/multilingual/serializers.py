from rest_framework import serializers
from .models import UserLanguagePreference, TranslationEntry
from .services.translation_service import TranslationService


class UserLanguagePreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLanguagePreference
        fields = ['id', 'preferred_language', 'auto_detect', 'font_size', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TranslationEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = TranslationEntry
        fields = ['id', 'key', 'language', 'value', 'context', 'is_approved', 'created_at']
        read_only_fields = ['id', 'created_at']


class TranslateRequestSerializer(serializers.Serializer):
    keys = serializers.ListField(child=serializers.CharField())
    language = serializers.CharField(max_length=5)


class TranslateResponseSerializer(serializers.Serializer):
    translations = serializers.DictField()
    language = serializers.CharField()
