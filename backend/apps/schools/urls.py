from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SchoolAcademicYearViewSet, SchoolViewSet

router = DefaultRouter()
router.register("schools", SchoolViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "schools/<int:school_pk>/academic-years/", SchoolAcademicYearViewSet.as_view({"get": "list", "post": "create"})
    ),
    path(
        "schools/<int:school_pk>/academic-years/<int:pk>/",
        SchoolAcademicYearViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
        ),
    ),
]
