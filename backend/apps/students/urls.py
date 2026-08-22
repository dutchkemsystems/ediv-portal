from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import StudentMedicalRecordViewSet, StudentParentViewSet, StudentViewSet

router = DefaultRouter()
router.register("students", StudentViewSet)
router.register("parents", StudentParentViewSet)
router.register("medical-records", StudentMedicalRecordViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
