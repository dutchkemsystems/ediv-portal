from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VehicleViewSet, BusRouteViewSet, StudentTransportViewSet

router = DefaultRouter()
router.register('vehicles', VehicleViewSet)
router.register('routes', BusRouteViewSet)
router.register('student-transport', StudentTransportViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
