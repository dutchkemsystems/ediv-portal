from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import JobPosting, JobApplication, PayrollPeriod, Payslip
from .serializers import (
    JobPostingSerializer, JobApplicationSerializer,
    PayrollPeriodSerializer, PayslipSerializer
)


class JobPostingViewSet(viewsets.ModelViewSet):
    queryset = JobPosting.objects.select_related('department', 'school', 'created_by').all()
    serializer_class = JobPostingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['department', 'school', 'status']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'closing_date']


class JobApplicationViewSet(viewsets.ModelViewSet):
    queryset = JobApplication.objects.select_related('job_posting', 'applicant', 'reviewed_by').all()
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['job_posting', 'status']
    search_fields = ['applicant__first_name', 'applicant__last_name']
    ordering_fields = ['created_at', 'review_date']


class PayrollPeriodViewSet(viewsets.ModelViewSet):
    queryset = PayrollPeriod.objects.all()
    serializer_class = PayrollPeriodSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['is_processed']
    ordering_fields = ['start_date', 'payment_date']


class PayslipViewSet(viewsets.ModelViewSet):
    queryset = Payslip.objects.select_related('staff__user', 'period').all()
    serializer_class = PayslipSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['staff', 'period', 'is_paid']
    search_fields = ['staff__user__first_name', 'staff__user__last_name']
    ordering_fields = ['period', 'created_at']
