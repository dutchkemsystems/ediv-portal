from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TranslationEntryViewSet, TranslationViewSet, UserLanguagePreferenceViewSet

router = DefaultRouter()
router.register("preferences", UserLanguagePreferenceViewSet, basename="language-preference")
router.register("entries", TranslationEntryViewSet, basename="translation-entry")
router.register("i18n", TranslationViewSet, basename="i18n")

urlpatterns = [
    path("", include(router.urls)),
]
