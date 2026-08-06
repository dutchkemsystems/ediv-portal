from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeviceTokenViewSet, PushNotificationViewSet, NotificationLogViewSet

router = DefaultRouter()
router.register('devices', DeviceTokenViewSet, basename='device-token')
router.register('notifications', PushNotificationViewSet, basename='push-notification')
router.register('logs', NotificationLogViewSet, basename='notification-log')

urlpatterns = [
    path('', include(router.urls)),
]
