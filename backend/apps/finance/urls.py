from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FeeStructureViewSet, StudentFeeViewSet, PaymentViewSet, BudgetViewSet
from .payment_views import InitializePaymentView, KoraPayWebhookView, VerifyPaymentView

router = DefaultRouter()
router.register('fee-structures', FeeStructureViewSet)
router.register('student-fees', StudentFeeViewSet)
router.register('payments', PaymentViewSet)
router.register('budgets', BudgetViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('payments/initialize/', InitializePaymentView.as_view(), name='payment-initialize'),
    path('payments/webhook/', KoraPayWebhookView.as_view(), name='payment-webhook'),
    path('payments/verify/<str:reference>/', VerifyPaymentView.as_view(), name='payment-verify'),
]
