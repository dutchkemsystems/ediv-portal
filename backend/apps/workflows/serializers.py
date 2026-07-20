from rest_framework import serializers
from .models import Workflow, WorkflowStep, WorkflowInstance, Task


class WorkflowStepSerializer(serializers.ModelSerializer):
    assigned_user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkflowStep
        fields = ['id', 'workflow', 'name', 'description', 'step_type', 'assigned_role',
                  'assigned_user', 'assigned_user_name', 'order', 'is_required',
                  'timeout_hours', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_assigned_user_name(self, obj):
        if obj.assigned_user:
            return obj.assigned_user.get_full_name()
        return None


class WorkflowSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    steps = WorkflowStepSerializer(many=True, read_only=True)
    
    class Meta:
        model = Workflow
        fields = ['id', 'name', 'description', 'created_by', 'created_by_name', 'status',
                  'trigger_type', 'trigger_config', 'is_template', 'steps',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name()


class TaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.SerializerMethodField()
    step_name = serializers.SerializerMethodField()
    workflow_reference = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = ['id', 'workflow_instance', 'step', 'step_name', 'assigned_to', 'assigned_to_name',
                  'status', 'comments', 'decision', 'due_date', 'completed_at',
                  'workflow_reference', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_assigned_to_name(self, obj):
        return obj.assigned_to.get_full_name()
    
    def get_step_name(self, obj):
        return obj.step.name
    
    def get_workflow_reference(self, obj):
        return obj.workflow_instance.reference_number


class WorkflowInstanceSerializer(serializers.ModelSerializer):
    initiated_by_name = serializers.SerializerMethodField()
    workflow_name = serializers.SerializerMethodField()
    current_step_name = serializers.SerializerMethodField()
    tasks = TaskSerializer(many=True, read_only=True)
    
    class Meta:
        model = WorkflowInstance
        fields = ['id', 'workflow', 'workflow_name', 'initiated_by', 'initiated_by_name',
                  'reference_number', 'status', 'current_step', 'current_step_name',
                  'data', 'tasks', 'started_at', 'completed_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'started_at', 'created_at', 'updated_at']
    
    def get_initiated_by_name(self, obj):
        return obj.initiated_by.get_full_name()
    
    def get_workflow_name(self, obj):
        return obj.workflow.name
    
    def get_current_step_name(self, obj):
        if obj.current_step:
            return obj.current_step.name
        return None

