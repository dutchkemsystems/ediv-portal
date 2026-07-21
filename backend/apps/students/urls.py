from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, StudentParentViewSet, StudentMedicalRecordViewSet

router = DefaultRouter()
router.register('students', StudentViewSet)
router.register('parents', StudentParentViewSet)
router.register('medical-records', StudentMedicalRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
