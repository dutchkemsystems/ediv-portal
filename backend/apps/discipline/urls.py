from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DisciplinaryIncidentViewSet, BehaviorPlanViewSet

router = DefaultRouter()
router.register('incidents', DisciplinaryIncidentViewSet)
router.register('behavior-plans', BehaviorPlanViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
