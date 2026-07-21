from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FacilityViewSet, MaintenanceRequestViewSet, ProjectViewSet

router = DefaultRouter()
router.register('facilities', FacilityViewSet)
router.register('maintenance-requests', MaintenanceRequestViewSet)
router.register('projects', ProjectViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
