from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import StudentAttendance, StaffAttendance, AttendanceSummary
from .serializers import (
    StudentAttendanceSerializer, StaffAttendanceSerializer,
    AttendanceSummarySerializer
)


class StudentAttendanceViewSet(viewsets.ModelViewSet):
    queryset = StudentAttendance.objects.select_related('student__user', 'recorded_by').all()
    serializer_class = StudentAttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'status', 'date']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    ordering_fields = ['date', 'created_at']


class StaffAttendanceViewSet(viewsets.ModelViewSet):
    queryset = StaffAttendance.objects.select_related('staff__user', 'recorded_by').all()
    serializer_class = StaffAttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['staff', 'status', 'date']
    search_fields = ['staff__user__first_name', 'staff__user__last_name']
    ordering_fields = ['date', 'created_at']


class AttendanceSummaryViewSet(viewsets.ModelViewSet):
    queryset = AttendanceSummary.objects.select_related('school').all()
    serializer_class = AttendanceSummarySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['school', 'academic_year', 'term']
    ordering_fields = ['academic_year', 'created_at']
