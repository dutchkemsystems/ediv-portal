from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationTemplateViewSet, NotificationLogViewSet

router = DefaultRouter()
router.register('templates', NotificationTemplateViewSet)
router.register('logs', NotificationLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
