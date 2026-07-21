from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Course, CourseModule, Lesson, Enrollment,
    Quiz, QuizQuestion, QuizAttempt
)
from .serializers import (
    CourseSerializer, CourseListSerializer, CourseModuleSerializer,
    LessonSerializer, EnrollmentSerializer, QuizSerializer,
    QuizQuestionSerializer, QuizAttemptSerializer
)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related('school', 'subject', 'instructor').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['school', 'subject', 'status']
    search_fields = ['title', 'code', 'description']
    ordering_fields = ['title', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CourseListSerializer
        return CourseSerializer


class CourseModuleViewSet(viewsets.ModelViewSet):
    queryset = CourseModule.objects.select_related('course').all()
    serializer_class = CourseModuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['course', 'is_active']
    ordering_fields = ['order', 'created_at']


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.select_related('module').all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['module', 'lesson_type', 'is_free']
    search_fields = ['title']
    ordering_fields = ['order', 'created_at']


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.select_related('course', 'student__user').all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['course', 'student', 'status']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    ordering_fields = ['enrollment_date', 'created_at']


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.select_related('lesson').all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['lesson', 'is_active']
    search_fields = ['title']
    ordering_fields = ['created_at']


class QuizQuestionViewSet(viewsets.ModelViewSet):
    queryset = QuizQuestion.objects.select_related('quiz').all()
    serializer_class = QuizQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['quiz', 'question_type']
    ordering_fields = ['order']


class QuizAttemptViewSet(viewsets.ModelViewSet):
    queryset = QuizAttempt.objects.select_related('quiz', 'student__user').all()
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['quiz', 'student', 'is_passed']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    ordering_fields = ['started_at', 'score']
