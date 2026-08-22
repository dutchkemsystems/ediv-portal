from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AccessDatabaseViewSet, ImportJobViewSet

router = DefaultRouter()
router.register("jobs", ImportJobViewSet, basename="importjob")
router.register("access-databases", AccessDatabaseViewSet, basename="accessdatabase")

urlpatterns = [
    path("", include(router.urls)),
]
