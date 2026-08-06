from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReportCardTemplateViewSet, GeneratedReportCardViewSet, ReportCardShareLogViewSet

router = DefaultRouter()
router.register('templates', ReportCardTemplateViewSet, basename='report-card-template')
router.register('reports', GeneratedReportCardViewSet, basename='generated-report-card')
router.register('share-logs', ReportCardShareLogViewSet, basename='report-card-share-log')

urlpatterns = [
    path('', include(router.urls)),
]
