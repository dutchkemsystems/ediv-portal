from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import StaffLeaveViewSet, StaffPerformanceViewSet, StaffViewSet

router = DefaultRouter()
router.register("staff", StaffViewSet)
router.register("leaves", StaffLeaveViewSet)
router.register("performances", StaffPerformanceViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
