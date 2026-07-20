from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnalyticsReportViewSet, KPIViewSet, DashboardStatsViewSet

router = DefaultRouter()
router.register('reports', AnalyticsReportViewSet)
router.register('kpis', KPIViewSet)
router.register('stats', DashboardStatsViewSet, basename='dashboard-stats')

urlpatterns = [
    path('', include(router.urls)),
]
