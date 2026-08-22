from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ActivityParticipantViewSet, ActivityViewSet, CompetitionEntryViewSet, CompetitionViewSet

router = DefaultRouter()
router.register("activities", ActivityViewSet)
router.register("participants", ActivityParticipantViewSet)
router.register("competitions", CompetitionViewSet)
router.register("competition-entries", CompetitionEntryViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
