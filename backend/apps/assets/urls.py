from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AssetMaintenanceViewSet, AssetTransferViewSet, AssetViewSet

router = DefaultRouter()
router.register("assets", AssetViewSet)
router.register("maintenance", AssetMaintenanceViewSet)
router.register("transfers", AssetTransferViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
