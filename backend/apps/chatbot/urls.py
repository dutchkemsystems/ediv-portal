from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ChatIntentViewSet, ChatSessionViewSet

router = DefaultRouter()
router.register("sessions", ChatSessionViewSet, basename="chat-session")
router.register("intents", ChatIntentViewSet, basename="chat-intent")

urlpatterns = [
    path("", include(router.urls)),
]
