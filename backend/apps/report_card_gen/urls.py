from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import GeneratedReportCardViewSet, ReportCardShareLogViewSet, ReportCardTemplateViewSet

router = DefaultRouter()
router.register("templates", ReportCardTemplateViewSet, basename="report-card-template")
router.register("reports", GeneratedReportCardViewSet, basename="generated-report-card")
router.register("share-logs", ReportCardShareLogViewSet, basename="report-card-share-log")

urlpatterns = [
    path("", include(router.urls)),
]
