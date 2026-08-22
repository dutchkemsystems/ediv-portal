from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AnalyticsReportViewSet, DashboardStatsViewSet, KPIViewSet

router = DefaultRouter()
router.register("reports", AnalyticsReportViewSet)
router.register("kpis", KPIViewSet)
router.register("stats", DashboardStatsViewSet, basename="dashboard-stats")

urlpatterns = [
    path("", include(router.urls)),
]
