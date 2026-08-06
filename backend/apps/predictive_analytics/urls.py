from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StudentRiskProfileViewSet, EarlyWarningAlertViewSet,
    InterventionViewSet, RiskTrendViewSet
)

router = DefaultRouter()
router.register('risk-profiles', StudentRiskProfileViewSet)
router.register('alerts', EarlyWarningAlertViewSet)
router.register('interventions', InterventionViewSet)
router.register('trends', RiskTrendViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
