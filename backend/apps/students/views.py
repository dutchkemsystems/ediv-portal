from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Student, StudentParent, StudentMedicalRecord
from .serializers import (
    StudentSerializer, StudentListSerializer,
    StudentParentSerializer, StudentMedicalRecordSerializer
)


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related('user', 'school', 'class_name').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['school', 'class_name', 'status', 'gender', 'is_boarding']
    search_fields = ['user__first_name', 'user__last_name', 'admission_number']
    ordering_fields = ['admission_number', 'admission_date', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return StudentListSerializer
        return StudentSerializer


class StudentParentViewSet(viewsets.ModelViewSet):
    queryset = StudentParent.objects.select_related('student__user', 'user').all()
    serializer_class = StudentParentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'relation', 'is_primary']


class StudentMedicalRecordViewSet(viewsets.ModelViewSet):
    queryset = StudentMedicalRecord.objects.select_related('student__user').all()
    serializer_class = StudentMedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student']
    search_fields = ['condition', 'student__user__first_name', 'student__user__last_name']
    ordering_fields = ['record_date', 'created_at']
