from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import UserLanguagePreference, TranslationEntry
from .serializers import (
    UserLanguagePreferenceSerializer, TranslationEntrySerializer,
    TranslateRequestSerializer
)
from .services.translation_service import TranslationService


class UserLanguagePreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = UserLanguagePreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserLanguagePreference.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


class TranslationEntryViewSet(viewsets.ModelViewSet):
    queryset = TranslationEntry.objects.all()
    serializer_class = TranslationEntrySerializer
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ['language', 'is_approved']
    search_fields = ['key', 'value']


class TranslationViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'], url_path='translate')
    def translate(self, request):
        serializer = TranslateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        keys = serializer.validated_data['keys']
        language = serializer.validated_data['language']
        translations = TranslationService.translate_batch(keys, language)
        return Response({
            'translations': translations,
            'language': language,
        })

    @action(detail=False, methods=['get'], url_path='languages')
    def languages(self, request):
        return Response(TranslationService.get_supported_languages())

    @action(detail=False, methods=['get'], url_path='keys')
    def keys(self, request):
        return Response({'keys': TranslationService.get_all_keys()})

    @action(detail=False, methods=['post'], url_path='detect')
    def detect_language(self, request):
        text = request.data.get('text', '')
        detected = TranslationService.detect_language(text)
        return Response({'detected_language': detected, 'text': text})

    @action(detail=False, methods=['post'], url_path='user-lang')
    def set_user_language(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        lang = request.data.get('language', 'en')
        pref, _ = UserLanguagePreference.objects.update_or_create(
            user=request.user,
            defaults={'preferred_language': lang}
        )
        return Response({'message': f'Language set to {lang}', 'language': lang})
