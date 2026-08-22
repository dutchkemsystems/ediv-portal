from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AcademicCalendarViewSet,
    ClassSubjectViewSet,
    ClassViewSet,
    ExamResultViewSet,
    ExamViewSet,
    ReportCardViewSet,
    StudentEnrollmentViewSet,
    SubjectViewSet,
)

router = DefaultRouter()
router.register("classes", ClassViewSet)
router.register("subjects", SubjectViewSet)
router.register("class-subjects", ClassSubjectViewSet)
router.register("exams", ExamViewSet)
router.register("exam-results", ExamResultViewSet)
router.register("report-cards", ReportCardViewSet)
router.register("calendar", AcademicCalendarViewSet)
router.register("enrollments", StudentEnrollmentViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
