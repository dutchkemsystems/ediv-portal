from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatSessionViewSet, ChatIntentViewSet

router = DefaultRouter()
router.register('sessions', ChatSessionViewSet, basename='chat-session')
router.register('intents', ChatIntentViewSet, basename='chat-intent')

urlpatterns = [
    path('', include(router.urls)),
]
