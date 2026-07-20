from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkflowViewSet, WorkflowStepViewSet, WorkflowInstanceViewSet, TaskViewSet

router = DefaultRouter()
router.register('workflows', WorkflowViewSet)
router.register('steps', WorkflowStepViewSet)
router.register('instances', WorkflowInstanceViewSet)
router.register('tasks', TaskViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
