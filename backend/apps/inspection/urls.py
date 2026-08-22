from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import InspectionActionViewSet, InspectionChecklistViewSet, InspectionViewSet

router = DefaultRouter()
router.register("inspections", InspectionViewSet)
router.register("checklists", InspectionChecklistViewSet)
router.register("actions", InspectionActionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
