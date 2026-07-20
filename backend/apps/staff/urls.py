from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StaffViewSet, StaffLeaveViewSet, StaffPerformanceViewSet

router = DefaultRouter()
router.register('staff', StaffViewSet)
router.register('leaves', StaffLeaveViewSet)
router.register('performances', StaffPerformanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
