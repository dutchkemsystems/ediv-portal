from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentAttendanceViewSet, StaffAttendanceViewSet, AttendanceSummaryViewSet

router = DefaultRouter()
router.register('student-attendance', StudentAttendanceViewSet)
router.register('staff-attendance', StaffAttendanceViewSet)
router.register('summaries', AttendanceSummaryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
