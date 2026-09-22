from rest_framework import permissions, viewsets

from config.permissions import IsHROrAdmin
from config.rbac import RoleBasedPermission, SchoolScopedQuerysetMixin

from .models import JobApplication, JobPosting, PayrollPeriod, Payslip
from .serializers import JobApplicationSerializer, JobPostingSerializer, PayrollPeriodSerializer, PayslipSerializer


class JobPostingViewSet(viewsets.ModelViewSet):
    queryset = JobPosting.objects.select_related("department", "school", "created_by").all()
    serializer_class = JobPostingSerializer
    rbac_app = "hr"
    permission_classes = [RoleBasedPermission]
    filterset_fields = ["department", "school", "status"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "closing_date"]


class JobApplicationViewSet(viewsets.ModelViewSet):
    queryset = JobApplication.objects.select_related("job_posting", "applicant", "reviewed_by").all()
    serializer_class = JobApplicationSerializer
    rbac_app = "hr"
    permission_classes = [RoleBasedPermission]
    filterset_fields = ["job_posting", "status"]
    search_fields = ["applicant__first_name", "applicant__last_name"]
    ordering_fields = ["created_at", "review_date"]


class PayrollPeriodViewSet(viewsets.ModelViewSet):
    queryset = PayrollPeriod.objects.all()
    serializer_class = PayrollPeriodSerializer
    rbac_app = "hr"
    permission_classes = [RoleBasedPermission]
    filterset_fields = ["is_processed"]
    ordering_fields = ["start_date", "payment_date"]


class PayslipViewSet(viewsets.ModelViewSet):
    queryset = Payslip.objects.select_related("staff__user", "period").all()
    serializer_class = PayslipSerializer
    rbac_app = "hr"
    permission_classes = [RoleBasedPermission]
    filterset_fields = ["staff", "period", "is_paid"]
    search_fields = ["staff__user__first_name", "staff__user__last_name"]
    ordering_fields = ["period", "created_at"]
