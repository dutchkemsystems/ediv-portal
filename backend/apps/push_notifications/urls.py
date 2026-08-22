from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DeviceTokenViewSet, NotificationLogViewSet, PushNotificationViewSet

router = DefaultRouter()
router.register("devices", DeviceTokenViewSet, basename="device-token")
router.register("notifications", PushNotificationViewSet, basename="push-notification")
router.register("logs", NotificationLogViewSet, basename="notification-log")

urlpatterns = [
    path("", include(router.urls)),
]
