from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import CounselingSession, WellnessCheckIn, WellnessResource
from .serializers import (
    CounselingSessionSerializer, WellnessCheckInSerializer,
    WellnessResourceSerializer
)


class CounselingSessionViewSet(viewsets.ModelViewSet):
    queryset = CounselingSession.objects.select_related('student__user', 'counselor').all()
    serializer_class = CounselingSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'counselor', 'counseling_type', 'session_date']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    ordering_fields = ['session_date', 'created_at']


class WellnessCheckInViewSet(viewsets.ModelViewSet):
    queryset = WellnessCheckIn.objects.select_related('student__user', 'flagged_by').all()
    serializer_class = WellnessCheckInSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'mood', 'is_flagged', 'date']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    ordering_fields = ['date', 'created_at']


class WellnessResourceViewSet(viewsets.ModelViewSet):
    queryset = WellnessResource.objects.all()
    serializer_class = WellnessResourceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['resource_type', 'is_emergency', 'is_active']
    search_fields = ['name', 'description']
