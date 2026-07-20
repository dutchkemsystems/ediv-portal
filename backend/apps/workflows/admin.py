from django.contrib import admin
from .models import Workflow, WorkflowStep, WorkflowInstance, Task


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'status', 'trigger_type', 'is_template']
    list_filter = ['status', 'trigger_type', 'is_template']
    search_fields = ['name', 'description']
    raw_id_fields = ['created_by']


@admin.register(WorkflowStep)
class WorkflowStepAdmin(admin.ModelAdmin):
    list_display = ['workflow', 'name', 'step_type', 'order', 'is_required']
    list_filter = ['step_type', 'is_required']
    raw_id_fields = ['workflow', 'assigned_user']


@admin.register(WorkflowInstance)
class WorkflowInstanceAdmin(admin.ModelAdmin):
    list_display = ['reference_number', 'workflow', 'initiated_by', 'status', 'started_at']
    list_filter = ['status']
    search_fields = ['reference_number']
    raw_id_fields = ['workflow', 'initiated_by', 'current_step']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['workflow_instance', 'step', 'assigned_to', 'status', 'decision', 'due_date']
    list_filter = ['status', 'decision']
    raw_id_fields = ['workflow_instance', 'step', 'assigned_to']
