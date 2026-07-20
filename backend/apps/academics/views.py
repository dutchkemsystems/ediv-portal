from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Class, Subject, ClassSubject, Exam, ExamResult, ReportCard,
    AcademicCalendar, StudentEnrollment
)
from .serializers import (
    ClassSerializer, ClassListSerializer, SubjectSerializer,
    ClassSubjectSerializer, ExamSerializer, ExamResultSerializer,
    ReportCardSerializer, AcademicCalendarSerializer, StudentEnrollmentSerializer
)


class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects.select_related('school', 'class_teacher').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['school', 'level', 'academic_year', 'term', 'is_active']
    search_fields = ['name', 'school__name']
    ordering_fields = ['name', 'level', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ClassListSerializer
        return ClassSerializer


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['category', 'is_compulsory']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code']


class ClassSubjectViewSet(viewsets.ModelViewSet):
    queryset = ClassSubject.objects.select_related('class_obj', 'subject', 'teacher').all()
    serializer_class = ClassSubjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['class_obj', 'subject', 'is_active']


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.select_related('school').all()
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['school', 'exam_type', 'academic_year', 'term', 'is_active']
    search_fields = ['name', 'school__name']
    ordering_fields = ['start_date', 'created_at']


class ExamResultViewSet(viewsets.ModelViewSet):
    queryset = ExamResult.objects.select_related('student__user', 'exam', 'subject', 'entered_by').all()
    serializer_class = ExamResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'exam', 'subject']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    ordering_fields = ['marks_obtained', 'entered_at']


class ReportCardViewSet(viewsets.ModelViewSet):
    queryset = ReportCard.objects.select_related('student__user').all()
    serializer_class = ReportCardSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'academic_year', 'term', 'is_released']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    ordering_fields = ['academic_year', 'class_position']


class AcademicCalendarViewSet(viewsets.ModelViewSet):
    queryset = AcademicCalendar.objects.select_related('school').all()
    serializer_class = AcademicCalendarSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['school', 'event_type', 'academic_year']
    search_fields = ['title', 'description']
    ordering_fields = ['start_date', 'created_at']


class StudentEnrollmentViewSet(viewsets.ModelViewSet):
    queryset = StudentEnrollment.objects.select_related('student__user', 'class_obj__school').all()
    serializer_class = StudentEnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['class_obj', 'academic_year', 'term', 'status']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    ordering_fields = ['enrollment_date', 'created_at']
