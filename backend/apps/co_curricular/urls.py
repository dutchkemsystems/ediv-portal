from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ActivityViewSet, ActivityParticipantViewSet,
    CompetitionViewSet, CompetitionEntryViewSet
)

router = DefaultRouter()
router.register('activities', ActivityViewSet)
router.register('participants', ActivityParticipantViewSet)
router.register('competitions', CompetitionViewSet)
router.register('competition-entries', CompetitionEntryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
