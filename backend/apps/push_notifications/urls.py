from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeviceTokenViewSet, PushNotificationViewSet, NotificationLogViewSet

router = DefaultRouter()
router.register('devices', DeviceTokenViewSet)
router.register('notifications', PushNotificationViewSet)
router.register('logs', NotificationLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
