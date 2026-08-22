from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BusRouteViewSet, StudentTransportViewSet, VehicleViewSet

router = DefaultRouter()
router.register("vehicles", VehicleViewSet)
router.register("routes", BusRouteViewSet)
router.register("student-transport", StudentTransportViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
