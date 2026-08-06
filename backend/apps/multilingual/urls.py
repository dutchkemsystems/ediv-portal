from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserLanguagePreferenceViewSet, TranslationEntryViewSet, TranslationViewSet

router = DefaultRouter()
router.register('preferences', UserLanguagePreferenceViewSet)
router.register('entries', TranslationEntryViewSet)
router.register('i18n', TranslationViewSet, basename='i18n')

urlpatterns = [
    path('', include(router.urls)),
]
