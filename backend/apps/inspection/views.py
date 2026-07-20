from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Inspection, InspectionChecklist, InspectionAction
from .serializers import (
    InspectionSerializer, InspectionListSerializer,
    InspectionChecklistSerializer, InspectionActionSerializer
)


class InspectionViewSet(viewsets.ModelViewSet):
    queryset = Inspection.objects.select_related('school', 'lead_inspector').prefetch_related('team_members').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['school', 'inspection_type', 'status']
    search_fields = ['title', 'school__name']
    ordering_fields = ['scheduled_date', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return InspectionListSerializer
        return InspectionSerializer


class InspectionChecklistViewSet(viewsets.ModelViewSet):
    queryset = InspectionChecklist.objects.select_related('inspection').all()
    serializer_class = InspectionChecklistSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['inspection', 'category', 'is_mandatory']
    search_fields = ['item', 'category']


class InspectionActionViewSet(viewsets.ModelViewSet):
    queryset = InspectionAction.objects.select_related('inspection', 'assigned_to').all()
    serializer_class = InspectionActionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['inspection', 'status', 'assigned_to']
    search_fields = ['action', 'description']
    ordering_fields = ['due_date', 'created_at']
