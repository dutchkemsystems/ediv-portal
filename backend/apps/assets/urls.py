from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssetViewSet, AssetMaintenanceViewSet, AssetTransferViewSet

router = DefaultRouter()
router.register('assets', AssetViewSet)
router.register('maintenance', AssetMaintenanceViewSet)
router.register('transfers', AssetTransferViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
