from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EarlyWarningAlertViewSet, InterventionViewSet, RiskTrendViewSet, StudentRiskProfileViewSet

router = DefaultRouter()
router.register("risk-profiles", StudentRiskProfileViewSet)
router.register("alerts", EarlyWarningAlertViewSet)
router.register("interventions", InterventionViewSet)
router.register("trends", RiskTrendViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
