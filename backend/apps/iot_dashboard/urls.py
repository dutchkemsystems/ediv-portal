from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SensorTypeViewSet, IoTDeviceViewSet, SensorReadingViewSet,
    AlertRuleViewSet, IoTAlertViewSet
)

router = DefaultRouter()
router.register('sensor-types', SensorTypeViewSet)
router.register('devices', IoTDeviceViewSet)
router.register('readings', SensorReadingViewSet)
router.register('alert-rules', AlertRuleViewSet)
router.register('alerts', IoTAlertViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
