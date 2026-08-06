from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserLanguagePreferenceViewSet, TranslationEntryViewSet, TranslationViewSet

router = DefaultRouter()
router.register('preferences', UserLanguagePreferenceViewSet, basename='language-preference')
router.register('entries', TranslationEntryViewSet, basename='translation-entry')
router.register('i18n', TranslationViewSet, basename='i18n')

urlpatterns = [
    path('', include(router.urls)),
]
