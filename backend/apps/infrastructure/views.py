from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Facility, MaintenanceRequest, Project
from .serializers import FacilitySerializer, MaintenanceRequestSerializer, ProjectSerializer


class FacilityViewSet(viewsets.ModelViewSet):
    queryset = Facility.objects.select_related('school').all()
    serializer_class = FacilitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['school', 'facility_type', 'condition', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']


class MaintenanceRequestViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceRequest.objects.select_related('facility', 'requested_by', 'assigned_to').all()
    serializer_class = MaintenanceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['facility', 'status', 'priority']
    search_fields = ['title', 'description']
    ordering_fields = ['priority', 'created_at']


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.select_related('school', 'project_manager').all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['school', 'status']
    search_fields = ['name', 'description']
    ordering_fields = ['start_date', 'created_at']
