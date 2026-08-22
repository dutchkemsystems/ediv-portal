from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CourseModuleViewSet,
    CourseViewSet,
    EnrollmentViewSet,
    LessonViewSet,
    QuizAttemptViewSet,
    QuizQuestionViewSet,
    QuizViewSet,
)

router = DefaultRouter()
router.register("courses", CourseViewSet)
router.register("modules", CourseModuleViewSet)
router.register("lessons", LessonViewSet)
router.register("enrollments", EnrollmentViewSet)
router.register("quizzes", QuizViewSet)
router.register("questions", QuizQuestionViewSet)
router.register("attempts", QuizAttemptViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
