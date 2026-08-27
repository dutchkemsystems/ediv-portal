from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .payment_views import InitializePaymentView, KoraPayWebhookView, VerifyPaymentView
from .views import (
    BudgetViewSet,
    FeeStructureViewSet,
    FinancialReportView,
    GrantViewSet,
    OutstandingBalanceView,
    PaymentViewSet,
    RevenueBySchoolView,
    StudentFeeViewSet,
)

router = DefaultRouter()
router.register("fee-structures", FeeStructureViewSet)
router.register("student-fees", StudentFeeViewSet)
router.register("payments", PaymentViewSet)
router.register("budgets", BudgetViewSet)
router.register("grants", GrantViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("payments/initialize/", InitializePaymentView.as_view(), name="payment-initialize"),
    path("payments/webhook/", KoraPayWebhookView.as_view(), name="payment-webhook"),
    path("payments/verify/<str:reference>/", VerifyPaymentView.as_view(), name="payment-verify"),
    path("reports/summary/", FinancialReportView.as_view(), name="financial-report-summary"),
    path("reports/by-school/", RevenueBySchoolView.as_view(), name="financial-report-by-school"),
    path("reports/outstanding/", OutstandingBalanceView.as_view(), name="financial-report-outstanding"),
]
