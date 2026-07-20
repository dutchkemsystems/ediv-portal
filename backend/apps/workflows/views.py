from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Workflow, WorkflowStep, WorkflowInstance, Task
from .serializers import (
    WorkflowSerializer, WorkflowStepSerializer,
    WorkflowInstanceSerializer, TaskSerializer
)


class WorkflowViewSet(viewsets.ModelViewSet):
    queryset = Workflow.objects.select_related('created_by').all()
    serializer_class = WorkflowSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'trigger_type', 'is_template']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']


class WorkflowStepViewSet(viewsets.ModelViewSet):
    queryset = WorkflowStep.objects.select_related('workflow', 'assigned_user').all()
    serializer_class = WorkflowStepSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['workflow', 'step_type', 'is_required']
    ordering_fields = ['order', 'created_at']


class WorkflowInstanceViewSet(viewsets.ModelViewSet):
    queryset = WorkflowInstance.objects.select_related('workflow', 'initiated_by', 'current_step').all()
    serializer_class = WorkflowInstanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['workflow', 'status', 'initiated_by']
    search_fields = ['reference_number']
    ordering_fields = ['started_at', 'created_at']


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.select_related('workflow_instance', 'step', 'assigned_to').all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['workflow_instance', 'assigned_to', 'status']
    search_fields = ['comments']
    ordering_fields = ['due_date', 'created_at']
