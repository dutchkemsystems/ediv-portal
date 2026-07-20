from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet, CourseModuleViewSet, LessonViewSet,
    EnrollmentViewSet, QuizViewSet, QuizQuestionViewSet, QuizAttemptViewSet
)

router = DefaultRouter()
router.register('courses', CourseViewSet)
router.register('modules', CourseModuleViewSet)
router.register('lessons', LessonViewSet)
router.register('enrollments', EnrollmentViewSet)
router.register('quizzes', QuizViewSet)
router.register('questions', QuizQuestionViewSet)
router.register('attempts', QuizAttemptViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
