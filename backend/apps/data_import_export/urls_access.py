from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AccessDatabaseViewSet

router = DefaultRouter()
router.register("", AccessDatabaseViewSet, basename="access-database")

urlpatterns = [
    path("", include(router.urls)),
]
