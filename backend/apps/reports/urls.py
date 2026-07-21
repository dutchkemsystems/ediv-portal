from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReportViewSet, DashboardViewSet, WidgetViewSet

router = DefaultRouter()
router.register('reports', ReportViewSet)
router.register('dashboards', DashboardViewSet)
router.register('widgets', WidgetViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
