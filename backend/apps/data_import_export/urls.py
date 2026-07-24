from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ImportJobViewSet

router = DefaultRouter()
router.register('jobs', ImportJobViewSet, basename='importjob')

urlpatterns = [
    path('', include(router.urls)),
]
