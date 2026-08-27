from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets

from config.permissions import IsAcademicStaff, IsSchoolManagementOrAbove

from .models import Staff, StaffLeave, StaffPerformance
from .serializers import StaffLeaveSerializer, StaffListSerializer, StaffPerformanceSerializer, StaffSerializer


class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.select_related("user", "school", "department").all()
    from config.permissions import IsAdminOrTGOrDeptHead
    permission_classes = [IsAdminOrTGOrDeptHead]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "designation", "employment_type", "school", "department", "is_active"]
    search_fields = ["user__first_name", "user__last_name", "staff_id", "employee_number"]
    ordering_fields = ["staff_id", "date_joined", "created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return StaffListSerializer
        return StaffSerializer


class StaffLeaveViewSet(viewsets.ModelViewSet):
    queryset = StaffLeave.objects.select_related("staff__user", "approved_by").all()
    serializer_class = StaffLeaveSerializer
    permission_classes = [IsSchoolManagementOrAbove]
    filterset_fields = ["leave_type", "status", "staff"]
    search_fields = ["staff__user__first_name", "staff__user__last_name"]
    ordering_fields = ["start_date", "created_at"]


class StaffPerformanceViewSet(viewsets.ModelViewSet):
    queryset = StaffPerformance.objects.select_related("staff__user", "reviewed_by").all()
    serializer_class = StaffPerformanceSerializer
    permission_classes = [IsSchoolManagementOrAbove]
    filterset_fields = ["academic_year", "term", "rating", "staff"]
    search_fields = ["staff__user__first_name", "staff__user__last_name"]
    ordering_fields = ["academic_year", "review_date"]
