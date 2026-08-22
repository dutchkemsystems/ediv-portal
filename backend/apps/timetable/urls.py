from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PeriodViewSet, TeacherTimetableViewSet, TimetableEntryViewSet, TimetableViewSet

router = DefaultRouter()
router.register("periods", PeriodViewSet)
router.register("timetables", TimetableViewSet)
router.register("entries", TimetableEntryViewSet)
router.register("teacher-timetables", TeacherTimetableViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
