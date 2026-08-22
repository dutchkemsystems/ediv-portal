from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AttendanceSummaryViewSet, StaffAttendanceViewSet, StudentAttendanceViewSet

router = DefaultRouter()
router.register("student-attendance", StudentAttendanceViewSet)
router.register("staff-attendance", StaffAttendanceViewSet)
router.register("summaries", AttendanceSummaryViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
