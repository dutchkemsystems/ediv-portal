from rest_framework import permissions, viewsets

from .models import BehaviorPlan, DisciplinaryIncident
from .serializers import BehaviorPlanSerializer, DisciplinaryIncidentSerializer


class DisciplinaryIncidentViewSet(viewsets.ModelViewSet):
    queryset = DisciplinaryIncident.objects.select_related("student__user", "reported_by").all()
    serializer_class = DisciplinaryIncidentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["student", "incident_type", "severity", "status"]
    search_fields = ["title", "description", "student__user__first_name", "student__user__last_name"]
    ordering_fields = ["incident_date", "created_at"]


class BehaviorPlanViewSet(viewsets.ModelViewSet):
    queryset = BehaviorPlan.objects.select_related("student__user", "created_by").all()
    serializer_class = BehaviorPlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["student", "is_active"]
    search_fields = ["title", "student__user__first_name", "student__user__last_name"]
    ordering_fields = ["start_date", "created_at"]
