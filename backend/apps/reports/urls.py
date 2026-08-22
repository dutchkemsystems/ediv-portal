from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DashboardViewSet, ReportViewSet, WidgetViewSet

router = DefaultRouter()
router.register("reports", ReportViewSet)
router.register("dashboards", DashboardViewSet)
router.register("widgets", WidgetViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
