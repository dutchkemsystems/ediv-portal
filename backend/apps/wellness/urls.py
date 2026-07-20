from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CounselingSessionViewSet, WellnessCheckInViewSet, WellnessResourceViewSet

router = DefaultRouter()
router.register('counseling-sessions', CounselingSessionViewSet)
router.register('check-ins', WellnessCheckInViewSet)
router.register('resources', WellnessResourceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
