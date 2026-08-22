from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CircularViewSet, MessageViewSet, UserNotificationViewSet

router = DefaultRouter()
router.register("messages", MessageViewSet)
router.register("notifications", UserNotificationViewSet)
router.register("circulars", CircularViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
