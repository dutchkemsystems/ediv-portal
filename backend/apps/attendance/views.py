from rest_framework import permissions, viewsets

from config.permissions import IsAcademicStaff, IsAdminOrTGOrDeptHead
from config.rbac import RoleBasedPermission, SchoolScopedQuerysetMixin

from .models import AttendanceSummary, StaffAttendance, StudentAttendance
from .serializers import AttendanceSummarySerializer, StaffAttendanceSerializer, StudentAttendanceSerializer


class StudentAttendanceViewSet(viewsets.ModelViewSet):
    queryset = StudentAttendance.objects.select_related("student__user", "recorded_by").all()
    serializer_class = StudentAttendanceSerializer
    rbac_app = "attendance"
    permission_classes = [RoleBasedPermission]
    filterset_fields = ["student", "status", "date"]
    search_fields = ["student__user__first_name", "student__user__last_name"]
    ordering_fields = ["date", "created_at"]


class StaffAttendanceViewSet(viewsets.ModelViewSet):
    queryset = StaffAttendance.objects.select_related("staff__user", "recorded_by").all()
    serializer_class = StaffAttendanceSerializer
    rbac_app = "attendance"
    permission_classes = [RoleBasedPermission]
    filterset_fields = ["staff", "status", "date"]
    search_fields = ["staff__user__first_name", "staff__user__last_name"]
    ordering_fields = ["date", "created_at"]


class AttendanceSummaryViewSet(SchoolScopedQuerysetMixin, viewsets.ModelViewSet):
    queryset = AttendanceSummary.objects.select_related("school").all()
    serializer_class = AttendanceSummarySerializer
    rbac_app = "attendance"
    permission_classes = [RoleBasedPermission]
    filterset_fields = ["school", "academic_year", "term"]
    ordering_fields = ["academic_year", "created_at"]
