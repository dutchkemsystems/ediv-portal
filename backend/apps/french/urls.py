from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FrenchClubMemberViewSet, FrenchClubViewSet, FrenchCompetitionViewSet, FrenchProgramViewSet

router = DefaultRouter()
router.register("programs", FrenchProgramViewSet)
router.register("clubs", FrenchClubViewSet)
router.register("members", FrenchClubMemberViewSet)
router.register("competitions", FrenchCompetitionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
