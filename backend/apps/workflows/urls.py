from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    TaskViewSet,
    WorkflowInstanceViewSet,
    WorkflowStepViewSet,
    WorkflowViewSet,
)
from .views_automation import (
    AssignmentAssignView,
    AssignmentConfigView,
    AssignmentPreviewView,
)

router = DefaultRouter()
router.register("workflows", WorkflowViewSet)
router.register("steps", WorkflowStepViewSet)
router.register("instances", WorkflowInstanceViewSet)
router.register("tasks", TaskViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "assignment/config/", AssignmentConfigView.as_view(), name="assignment-config"
    ),
    path(
        "assignment/preview/",
        AssignmentPreviewView.as_view(),
        name="assignment-preview",
    ),
    path(
        "assignment/assign/", AssignmentAssignView.as_view(), name="assignment-assign"
    ),
]
