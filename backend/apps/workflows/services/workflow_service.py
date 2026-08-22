"""Workflow engine service: seed, start, advance, and task assignment."""

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.workflows.models import Task, Workflow, WorkflowInstance, WorkflowStep
from apps.workflows.workflow_definitions import ALL_WORKFLOWS

User = get_user_model()

# Map workflow-definition roles to real User.Role values.
ROLE_MAPPING = {
    "TG": "TG_PS",
    "MAIL_ROOM": "REG_OFF",
    "REGISTRAR": "REG_OFF",
    "DEPT_HEAD": "REG",
    "SUPERVISOR": "REG",
    "LEGAL": "REG",
    "STAFF": "SA_OFF",
    "DEPT_STAFF": "SA_OFF",
    "SCHOOL_STAFF": "SA_OFF",
    "HQ_STAFF": "REG_OFF",
    "PRINCIPAL": "PRI",
    "RECIPIENT": "REG_OFF",
    "CREATOR": "SA_OFF",
}

# Workflow-step action names that represent approval decisions.
APPROVAL_ACTIONS = {
    "APPROVED",
    "APPROVAL",
    "FINAL_APPROVAL",
    "TG_APPROVAL",
    "DEPT_HEAD_APPROVAL",
    "DEPT_APPROVAL",
    "PRINCIPAL_REVIEW",
}


class WorkflowService:
    """Creates, starts, and advances workflow instances from configured definitions."""

    @staticmethod
    def map_role(role):
        """Translate a workflow-definition role to a real User.Role value."""
        if role in User.Role.values:
            return role
        return ROLE_MAPPING.get(role, "")

    @staticmethod
    def seed_all(*, created_by=None, overwrite=False) -> dict:
        """Create Workflow + WorkflowStep rows from ALL_WORKFLOWS definitions."""
        if created_by is None:
            created_by = User.objects.filter(role="SYSADMIN").order_by("id").first()
        if created_by is None:
            raise ValueError("No SYSADMIN user available to own seeded workflows.")

        stats = {"created": 0, "updated": 0}
        for wf_type, definition in ALL_WORKFLOWS.items():
            workflow, created = Workflow.objects.get_or_create(
                name=definition["name"],
                defaults={
                    "description": definition["description"],
                    "created_by": created_by,
                    "status": "ACTIVE",
                    "is_template": True,
                    "trigger_config": {"workflow_type": wf_type},
                },
            )
            if not created and overwrite:
                workflow.description = definition["description"]
                workflow.trigger_config = {"workflow_type": wf_type}
                workflow.status = "ACTIVE"
                workflow.is_template = True
                workflow.save(update_fields=["description", "trigger_config", "status", "is_template"])

            if created:
                stats["created"] += 1
            else:
                stats["updated"] += 1

            for step_def in definition["steps"]:
                role = WorkflowService.map_role(step_def.get("required_role", ""))
                step_type = "APPROVAL" if step_def.get("action") in APPROVAL_ACTIONS else "ROUTING"
                _, step_created = WorkflowStep.objects.get_or_create(
                    workflow=workflow,
                    order=step_def["order"],
                    defaults={
                        "name": step_def["name"],
                        "description": step_def["description"],
                        "step_type": step_type,
                        "assigned_role": role,
                        "is_required": True,
                    },
                )
                if not step_created and overwrite:
                    workflow.steps.filter(order=step_def["order"]).update(
                        name=step_def["name"],
                        description=step_def["description"],
                        step_type=step_type,
                        assigned_role=role,
                    )

        return stats

    @staticmethod
    def get_workflow_by_type(workflow_type):
        """Return the active Workflow row for a configured workflow type."""
        for wf in Workflow.objects.filter(status="ACTIVE"):
            if wf.trigger_config.get("workflow_type") == workflow_type:
                return wf
        return None

    @staticmethod
    @transaction.atomic
    def start_instance(*, workflow_type, initiated_by, reference_number, data=None) -> WorkflowInstance:
        """Create a WorkflowInstance for a workflow type and assign its first task."""
        workflow = WorkflowService.get_workflow_by_type(workflow_type)
        if workflow is None:
            raise ValueError(f"No active workflow found for type: {workflow_type}")

        instance = WorkflowInstance.objects.create(
            workflow=workflow,
            initiated_by=initiated_by,
            reference_number=reference_number,
            status="PENDING",
            data=data or {},
        )

        first_step = workflow.steps.order_by("order").first()
        if first_step:
            instance.current_step = first_step
            instance.status = "IN_PROGRESS"
            instance.save(update_fields=["current_step", "status", "updated_at"])
            WorkflowService._assign_task(instance, first_step)

        return instance

    @staticmethod
    @transaction.atomic
    def advance(instance, *, user, decision="APPROVE", comments="") -> dict:
        """Complete the current task and move to the next step (or complete the workflow)."""
        if instance.status in ("COMPLETED", "CANCELLED"):
            raise ValueError(f"Workflow is already {instance.status}.")

        if instance.current_step is None:
            raise ValueError("Workflow has no current step.")

        current_task = (
            Task.objects.filter(
                workflow_instance=instance,
                step=instance.current_step,
                status__in=["PENDING", "IN_PROGRESS"],
            )
            .order_by("id")
            .first()
        )

        if current_task:
            if current_task.assigned_to != user and not user.is_superuser and user.role != "SYSADMIN":
                raise ValueError(f"User {user.email} is not assigned to step {instance.current_step.name}.")
            current_task.status = "COMPLETED"
            current_task.decision = decision
            current_task.comments = comments
            current_task.completed_at = timezone.now()
            current_task.save(update_fields=["status", "decision", "comments", "completed_at"])

        next_step = instance.workflow.steps.filter(order__gt=instance.current_step.order).order_by("order").first()

        if next_step is None:
            instance.status = "COMPLETED"
            instance.current_step = None
            instance.completed_at = timezone.now()
            instance.save(update_fields=["status", "current_step", "completed_at", "updated_at"])
            return {"status": "COMPLETED", "instance_id": instance.id}

        instance.current_step = next_step
        instance.status = "IN_PROGRESS"
        instance.save(update_fields=["current_step", "status", "updated_at"])
        WorkflowService._assign_task(instance, next_step)
        return {
            "status": "IN_PROGRESS",
            "instance_id": instance.id,
            "next_step": next_step.name,
        }

    @staticmethod
    def _assign_task(instance, step):
        """Assign a task for the given step to a matching-role user (or SYSADMIN)."""
        assignee = None
        if step.assigned_role:
            assignee = User.objects.filter(role=step.assigned_role, is_active=True).order_by("id").first()
        if assignee is None:
            assignee = User.objects.filter(role="SYSADMIN", is_active=True).order_by("id").first()
        if assignee is None:
            assignee = instance.initiated_by

        return Task.objects.create(
            workflow_instance=instance,
            step=step,
            assigned_to=assignee,
            status="PENDING",
        )
