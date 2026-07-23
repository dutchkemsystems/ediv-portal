from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuditLogViewSet, ComplianceItemViewSet, ComplianceRecordViewSet, ViolationViewSet

router = DefaultRouter()
router.register('logs', AuditLogViewSet)
router.register('compliance-items', ComplianceItemViewSet)
router.register('compliance-records', ComplianceRecordViewSet)
router.register('violations', ViolationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
