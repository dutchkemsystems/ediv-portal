from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TaskViewSet, WorkflowInstanceViewSet, WorkflowStepViewSet, WorkflowViewSet

router = DefaultRouter()
router.register("workflows", WorkflowViewSet)
router.register("steps", WorkflowStepViewSet)
router.register("instances", WorkflowInstanceViewSet)
router.register("tasks", TaskViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
