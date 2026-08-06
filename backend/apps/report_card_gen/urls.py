from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReportCardTemplateViewSet, GeneratedReportCardViewSet, ReportCardShareLogViewSet

router = DefaultRouter()
router.register('templates', ReportCardTemplateViewSet)
router.register('reports', GeneratedReportCardViewSet)
router.register('share-logs', ReportCardShareLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
