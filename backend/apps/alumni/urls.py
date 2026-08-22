from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AlumniDonationViewSet, AlumniEventViewSet, AlumniMemberViewSet

router = DefaultRouter()
router.register("members", AlumniMemberViewSet)
router.register("events", AlumniEventViewSet)
router.register("donations", AlumniDonationViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
