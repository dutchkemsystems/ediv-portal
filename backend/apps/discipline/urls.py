from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BehaviorPlanViewSet, DisciplinaryIncidentViewSet

router = DefaultRouter()
router.register("incidents", DisciplinaryIncidentViewSet)
router.register("behavior-plans", BehaviorPlanViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
