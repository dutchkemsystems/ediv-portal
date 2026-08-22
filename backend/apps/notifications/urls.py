from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import NotificationLogViewSet, NotificationTemplateViewSet

router = DefaultRouter()
router.register("templates", NotificationTemplateViewSet)
router.register("logs", NotificationLogViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
