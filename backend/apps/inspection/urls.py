from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InspectionViewSet, InspectionChecklistViewSet, InspectionActionViewSet

router = DefaultRouter()
router.register('inspections', InspectionViewSet)
router.register('checklists', InspectionChecklistViewSet)
router.register('actions', InspectionActionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
