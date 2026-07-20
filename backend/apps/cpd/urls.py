from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CPDActivityViewSet, CPDEnrollmentViewSet, CPDRecordViewSet

router = DefaultRouter()
router.register('activities', CPDActivityViewSet)
router.register('enrollments', CPDEnrollmentViewSet)
router.register('records', CPDRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
