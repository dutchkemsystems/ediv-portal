from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets

from config.permissions import IsAdminOrTGOrDeptHead, IsSchoolStaffOrAdmin
from config.rbac import RoleBasedPermission, SchoolScopedQuerysetMixin

from .models import Student, StudentMedicalRecord, StudentParent
from .serializers import (
    StudentListSerializer,
    StudentMedicalRecordSerializer,
    StudentParentSerializer,
    StudentSerializer,
)


class StudentViewSet(SchoolScopedQuerysetMixin, viewsets.ModelViewSet):
    queryset = Student.objects.select_related("user", "school", "class_name").all()
    rbac_app = "students"
    permission_classes = [RoleBasedPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["school", "class_name", "status", "gender", "is_boarding"]
    search_fields = ["user__first_name", "user__last_name", "admission_number"]
    ordering_fields = ["admission_number", "admission_date", "created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return StudentListSerializer
        return StudentSerializer


class StudentParentViewSet(viewsets.ModelViewSet):
    queryset = StudentParent.objects.select_related("student__user", "user").all()
    serializer_class = StudentParentSerializer
    rbac_app = "students"
    permission_classes = [RoleBasedPermission]
    filterset_fields = ["student", "relation", "is_primary"]


class StudentMedicalRecordViewSet(viewsets.ModelViewSet):
    queryset = StudentMedicalRecord.objects.select_related("student__user").all()
    serializer_class = StudentMedicalRecordSerializer
    from config.permissions import IsAdminOrTGOrDeptHead

    permission_classes = [IsAdminOrTGOrDeptHead]
    filterset_fields = ["student"]
    search_fields = ["condition", "student__user__first_name", "student__user__last_name"]
    ordering_fields = ["record_date", "created_at"]
