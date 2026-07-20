from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MessageViewSet, UserNotificationViewSet, CircularViewSet

router = DefaultRouter()
router.register('messages', MessageViewSet)
router.register('notifications', UserNotificationViewSet)
router.register('circulars', CircularViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
