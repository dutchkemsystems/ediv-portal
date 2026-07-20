from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FrenchProgramViewSet, FrenchClubViewSet, FrenchClubMemberViewSet, FrenchCompetitionViewSet

router = DefaultRouter()
router.register('programs', FrenchProgramViewSet)
router.register('clubs', FrenchClubViewSet)
router.register('members', FrenchClubMemberViewSet)
router.register('competitions', FrenchCompetitionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
