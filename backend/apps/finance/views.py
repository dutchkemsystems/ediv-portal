from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import FeeStructure, StudentFee, Payment, Budget
from .serializers import (
    FeeStructureSerializer, StudentFeeSerializer,
    PaymentSerializer, BudgetSerializer
)


class FeeStructureViewSet(viewsets.ModelViewSet):
    queryset = FeeStructure.objects.select_related('school').all()
    serializer_class = FeeStructureSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['school', 'fee_type', 'academic_year', 'term', 'is_active']
    search_fields = ['name', 'school__name']
    ordering_fields = ['amount', 'created_at']


class StudentFeeViewSet(viewsets.ModelViewSet):
    queryset = StudentFee.objects.select_related('student__user', 'fee_structure').all()
    serializer_class = StudentFeeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'fee_structure', 'status']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    ordering_fields = ['amount_due', 'created_at']


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related(
        'student_fee__student__user', 'student_fee__fee_structure',
        'received_by', 'confirmed_by'
    ).all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['payment_method', 'is_confirmed', 'payment_date']
    search_fields = ['reference_number', 'student_fee__student__user__first_name']
    ordering_fields = ['payment_date', 'amount', 'created_at']


class BudgetViewSet(viewsets.ModelViewSet):
    queryset = Budget.objects.select_related('school', 'approved_by').all()
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['school', 'category', 'academic_year', 'term', 'is_approved']
    search_fields = ['description', 'school__name']
    ordering_fields = ['allocated_amount', 'created_at']
