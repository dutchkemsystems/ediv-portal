from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlumniMemberViewSet, AlumniEventViewSet, AlumniDonationViewSet

router = DefaultRouter()
router.register('members', AlumniMemberViewSet)
router.register('events', AlumniEventViewSet)
router.register('donations', AlumniDonationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
