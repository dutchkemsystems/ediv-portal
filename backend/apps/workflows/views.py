from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions
from rest_framework import status as http_status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from config.permissions import IsAdminOrTGOrDeptHead

from .models import Task, Workflow, WorkflowInstance, WorkflowStep
from .serializers import TaskSerializer, WorkflowInstanceSerializer, WorkflowSerializer, WorkflowStepSerializer
from .services.workflow_service import WorkflowService


class WorkflowViewSet(viewsets.ModelViewSet):
    queryset = Workflow.objects.select_related("created_by").all()
    serializer_class = WorkflowSerializer
    permission_classes = [IsAdminOrTGOrDeptHead]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "trigger_type", "is_template"]
    search_fields = ["name", "description"]
    ordering_fields = ["created_at", "name"]


class WorkflowStepViewSet(viewsets.ModelViewSet):
    queryset = WorkflowStep.objects.select_related("workflow", "assigned_user").all()
    serializer_class = WorkflowStepSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["workflow", "step_type", "is_required"]
    ordering_fields = ["order", "created_at"]


class WorkflowInstanceViewSet(viewsets.ModelViewSet):
    queryset = WorkflowInstance.objects.select_related("workflow", "initiated_by", "current_step").all()
    serializer_class = WorkflowInstanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["workflow", "status", "initiated_by"]
    search_fields = ["reference_number"]
    ordering_fields = ["started_at", "created_at"]

    @action(detail=False, methods=["post"])
    def start(self, request):
        """Start a workflow instance from a configured workflow type."""
        workflow_type = request.data.get("workflow_type")
        reference_number = request.data.get("reference_number")
        if not workflow_type or not reference_number:
            return Response(
                {"error": "workflow_type and reference_number are required."},
                status=http_status.HTTP_400_BAD_REQUEST,
            )
        try:
            instance = WorkflowService.start_instance(
                workflow_type=workflow_type,
                initiated_by=request.user,
                reference_number=reference_number,
                data=request.data.get("data"),
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=http_status.HTTP_400_BAD_REQUEST)
        return Response(
            WorkflowInstanceSerializer(instance).data,
            status=http_status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def advance(self, request, pk=None):
        """Complete the current task and move to the next step or complete the workflow."""
        instance = self.get_object()
        try:
            result = WorkflowService.advance(
                instance,
                user=request.user,
                decision=request.data.get("decision", "APPROVE"),
                comments=request.data.get("comments", ""),
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=http_status.HTTP_400_BAD_REQUEST)
        return Response(result)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.select_related("workflow_instance", "step", "assigned_to").all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["workflow_instance", "assigned_to", "status"]
    search_fields = ["comments"]
    ordering_fields = ["due_date", "created_at"]
