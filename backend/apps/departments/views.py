from rest_framework import permissions, viewsets

from config.permissions import IsAdminOrTGOrDeptHead

from .models import Department, Unit
from .serializers import DepartmentListSerializer, DepartmentSerializer, UnitSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    permission_classes = [IsAdminOrTGOrDeptHead]
    filterset_fields = ["category", "is_active"]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return DepartmentListSerializer
        return DepartmentSerializer


class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.select_related("department", "head").all()
    serializer_class = UnitSerializer
    permission_classes = [IsAdminOrTGOrDeptHead]
    filterset_fields = ["department", "is_active"]
    search_fields = ["name", "code"]
