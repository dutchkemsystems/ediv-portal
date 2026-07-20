from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import DisciplinaryIncident, BehaviorPlan
from .serializers import DisciplinaryIncidentSerializer, BehaviorPlanSerializer


class DisciplinaryIncidentViewSet(viewsets.ModelViewSet):
    queryset = DisciplinaryIncident.objects.select_related('student__user', 'reported_by').all()
    serializer_class = DisciplinaryIncidentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'incident_type', 'severity', 'status']
    search_fields = ['title', 'description', 'student__user__first_name', 'student__user__last_name']
    ordering_fields = ['incident_date', 'created_at']


class BehaviorPlanViewSet(viewsets.ModelViewSet):
    queryset = BehaviorPlan.objects.select_related('student__user', 'created_by').all()
    serializer_class = BehaviorPlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'is_active']
    search_fields = ['title', 'student__user__first_name', 'student__user__last_name']
    ordering_fields = ['start_date', 'created_at']
