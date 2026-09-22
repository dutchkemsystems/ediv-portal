from django.db import models as db_models
from django.db.models import Sum
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from config.permissions import IsAdminOrTGOrDeptHead, IsFinanceOrAdmin
from config.rbac import RoleBasedPermission, SchoolScopedQuerysetMixin

from .models import Budget, FeeStructure, Grant, Payment, StudentFee
from .serializers import (
    BudgetSerializer,
    FeeStructureSerializer,
    GrantListSerializer,
    GrantSerializer,
    PaymentSerializer,
    StudentFeeSerializer,
)


class FeeStructureViewSet(SchoolScopedQuerysetMixin, viewsets.ModelViewSet):
    queryset = FeeStructure.objects.select_related("school").all()
    serializer_class = FeeStructureSerializer
    rbac_app = "finance"
    permission_classes = [RoleBasedPermission]
    filterset_fields = ["school", "fee_type", "academic_year", "term", "is_active"]
    search_fields = ["name", "school__name"]
    ordering_fields = ["amount", "created_at"]


class StudentFeeViewSet(SchoolScopedQuerysetMixin, viewsets.ModelViewSet):
    queryset = StudentFee.objects.select_related("student__user", "fee_structure").all()
    serializer_class = StudentFeeSerializer
    rbac_app = "finance"
    permission_classes = [RoleBasedPermission]
    school_filter_field = "fee_structure__school"
    filterset_fields = ["student", "fee_structure", "status"]
    search_fields = ["student__user__first_name", "student__user__last_name"]
    ordering_fields = ["amount_due", "created_at"]


class PaymentViewSet(SchoolScopedQuerysetMixin, viewsets.ModelViewSet):
    queryset = Payment.objects.select_related(
        "student_fee__student__user", "student_fee__fee_structure", "received_by", "confirmed_by"
    ).all()
    serializer_class = PaymentSerializer
    rbac_app = "finance"
    permission_classes = [RoleBasedPermission]
    school_filter_field = "student_fee__fee_structure__school"
    filterset_fields = ["payment_method", "is_confirmed", "payment_date"]
    search_fields = ["reference_number", "student_fee__student__user__first_name"]
    ordering_fields = ["payment_date", "amount", "created_at"]


class BudgetViewSet(SchoolScopedQuerysetMixin, viewsets.ModelViewSet):
    queryset = Budget.objects.select_related("school", "approved_by").all()
    serializer_class = BudgetSerializer
    rbac_app = "finance"
    permission_classes = [RoleBasedPermission]
    filterset_fields = ["school", "category", "academic_year", "term", "is_approved"]
    search_fields = ["description", "school__name"]
    ordering_fields = ["allocated_amount", "created_at"]


class GrantViewSet(SchoolScopedQuerysetMixin, viewsets.ModelViewSet):
    queryset = Grant.objects.select_related("school", "department", "approved_by", "created_by").all()
    rbac_app = "finance"
    permission_classes = [RoleBasedPermission]
    filterset_fields = ["status", "school", "department", "academic_year", "is_active"]
    search_fields = ["name", "funding_source", "purpose"]
    ordering_fields = ["amount", "created_at", "status"]

    def get_serializer_class(self):
        if self.action == "list":
            return GrantListSerializer
        return GrantSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class FinancialReportView(APIView):
    """Financial summary report endpoint."""

    rbac_app = "finance"
    permission_classes = [RoleBasedPermission]

    def get(self, request):
        school_id = request.query_params.get("school_id")
        academic_year = request.query_params.get("academic_year")
        term = request.query_params.get("term")

        fees_qs = StudentFee.objects.all()
        payments_qs = Payment.objects.filter(is_confirmed=True)

        if school_id:
            fees_qs = fees_qs.filter(fee_structure__school_id=school_id)
            payments_qs = payments_qs.filter(student_fee__fee_structure__school_id=school_id)
        if academic_year:
            fees_qs = fees_qs.filter(fee_structure__academic_year=academic_year)
            payments_qs = payments_qs.filter(student_fee__fee_structure__academic_year=academic_year)
        if term:
            fees_qs = fees_qs.filter(fee_structure__term=term)
            payments_qs = payments_qs.filter(student_fee__fee_structure__term=term)

        total_due = fees_qs.aggregate(total=Sum("amount_due"))["total"] or 0
        total_paid = fees_qs.aggregate(total=Sum("amount_paid"))["total"] or 0
        total_balance = total_due - total_paid

        by_status = dict(
            fees_qs.values_list("status").annotate(count=db_models.Count("id")).values_list("status", "count")
        )

        by_fee_type = list(
            fees_qs.values("fee_structure__fee_type")
            .annotate(
                total_due=Sum("amount_due"),
                total_paid=Sum("amount_paid"),
                count=db_models.Count("id"),
            )
            .order_by("fee_structure__fee_type")
        )

        recent_payments = payments_qs.select_related(
            "student_fee__student__user", "student_fee__fee_structure"
        ).order_by("-payment_date")[:20]

        return Response(
            {
                "summary": {
                    "total_due": float(total_due),
                    "total_paid": float(total_paid),
                    "total_balance": float(total_balance),
                    "collection_rate": round((total_paid / total_due * 100), 2) if total_due > 0 else 0,
                    "total_fees": fees_qs.count(),
                },
                "by_status": by_status,
                "by_fee_type": by_fee_type,
                "recent_payments": PaymentSerializer(recent_payments, many=True).data,
            }
        )


class RevenueBySchoolView(APIView):
    """Revenue breakdown by school."""

    rbac_app = "finance"
    permission_classes = [RoleBasedPermission]

    def get(self, request):
        academic_year = request.query_params.get("academic_year")
        term = request.query_params.get("term")

        qs = StudentFee.objects.filter(is_confirmed=True)
        if academic_year:
            qs = qs.filter(fee_structure__academic_year=academic_year)
        if term:
            qs = qs.filter(fee_structure__term=term)

        by_school = list(
            qs.values("fee_structure__school__name", "fee_structure__school__code")
            .annotate(
                total_due=Sum("amount_due"),
                total_paid=Sum("amount_paid"),
                count=db_models.Count("id"),
            )
            .order_by("-total_paid")
        )

        return Response({"schools": by_school})


class OutstandingBalanceView(APIView):
    """Outstanding balances by student."""

    rbac_app = "finance"
    permission_classes = [RoleBasedPermission]

    def get(self, request):
        school_id = request.query_params.get("school_id")
        limit = int(request.query_params.get("limit", 50))

        qs = StudentFee.objects.filter(status__in=["PENDING", "PARTIAL"]).select_related(
            "student__user", "fee_structure__school"
        )

        if school_id:
            qs = qs.filter(fee_structure__school_id=school_id)

        outstanding = qs.order_by("-balance")[:limit]

        data = [
            {
                "student_id": sf.student_id,
                "student_name": sf.student.user.get_full_name(),
                "school": sf.fee_structure.school.name,
                "fee_name": sf.fee_structure.name,
                "amount_due": float(sf.amount_due),
                "amount_paid": float(sf.amount_paid),
                "balance": float(sf.balance),
                "status": sf.status,
            }
            for sf in outstanding
        ]

        return Response({"count": len(data), "outstanding": data})
