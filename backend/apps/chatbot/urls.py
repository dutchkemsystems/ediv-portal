from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatSessionViewSet, ChatIntentViewSet

router = DefaultRouter()
router.register('sessions', ChatSessionViewSet)
router.register('intents', ChatIntentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
