from django.db import models
from django.conf import settings


class WorkflowStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Draft'
    ACTIVE = 'ACTIVE', 'Active'
    COMPLETED = 'COMPLETED', 'Completed'
    CANCELLED = 'CANCELLED', 'Cancelled'
    ON_HOLD = 'ON_HOLD', 'On Hold'


class TaskStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    COMPLETED = 'COMPLETED', 'Completed'
    BLOCKED = 'BLOCKED', 'Blocked'
    CANCELLED = 'CANCELLED', 'Cancelled'


class Workflow(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_workflows'
    )
    status = models.CharField(max_length=20, choices=WorkflowStatus.choices, default='DRAFT')
    trigger_type = models.CharField(max_length=20, choices=[
        ('MANUAL', 'Manual'),
        ('AUTOMATIC', 'Automatic'),
        ('SCHEDULED', 'Scheduled'),
    ], default='MANUAL')
    trigger_config = models.JSONField(default=dict)
    is_template = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_by']),
        ]
    
    def __str__(self):
        return self.name


class WorkflowStep(models.Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='steps')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    step_type = models.CharField(max_length=20, choices=[
        ('APPROVAL', 'Approval'),
        ('REVIEW', 'Review'),
        ('ACTION', 'Action'),
        ('NOTIFICATION', 'Notification'),
        ('ROUTING', 'Routing'),
    ])
    assigned_role = models.CharField(max_length=20, blank=True)
    assigned_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='workflow_steps'
    )
    order = models.IntegerField(default=0)
    is_required = models.BooleanField(default=True)
    timeout_hours = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['workflow', 'order']
    
    def __str__(self):
        return f"{self.workflow.name} - Step {self.order}: {self.name}"


class WorkflowInstance(models.Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='instances')
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='initiated_workflows'
    )
    reference_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=TaskStatus.choices, default='PENDING')
    current_step = models.ForeignKey(WorkflowStep, on_delete=models.SET_NULL, null=True, blank=True)
    data = models.JSONField(default=dict)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['reference_number']),
            models.Index(fields=['status']),
            models.Index(fields=['initiated_by']),
        ]
    
    def __str__(self):
        return f"{self.reference_number} - {self.workflow.name}"


class Task(models.Model):
    workflow_instance = models.ForeignKey(WorkflowInstance, on_delete=models.CASCADE, related_name='tasks')
    step = models.ForeignKey(WorkflowStep, on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_tasks'
    )
    status = models.CharField(max_length=20, choices=TaskStatus.choices, default='PENDING')
    comments = models.TextField(blank=True)
    decision = models.CharField(max_length=20, choices=[
        ('APPROVE', 'Approve'),
        ('REJECT', 'Reject'),
        ('RETURN', 'Return'),
        ('NONE', 'None'),
    ], blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['assigned_to']),
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"{self.workflow_instance.reference_number} - {self.step.name}"
