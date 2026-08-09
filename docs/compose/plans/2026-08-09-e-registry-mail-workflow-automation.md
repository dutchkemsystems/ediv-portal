# E-Registry + Mail Workflow Automation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use SKILL:subagent-dev (recommended) or SKILL:execute-plan to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete Wave 4 (Document Management) by wiring the configured workflow engine into E-Registry and Mail Workflow. Connect `backend/apps/workflows/workflow_definitions.py` (7 pre-configured multi-step workflows) to the `Workflow`/`WorkflowInstance`/`Task` models, expose the missing memo/movement sub-models as API viewsets, and add comprehensive tests.

**Architecture:** A `WorkflowService` in `apps/workflows/services/` seeds definitions, starts instances, advances steps, and creates/auto-assigns tasks. The registry and mail_workflow viewsets stay thin; the service owns state transitions. MemoApproval/MemoCirculation and the four movement models get dedicated read/create viewsets registered in existing routers.

**Tech Stack:** Django 4.2, DRF, PostgreSQL, in-memory SQLite tests

---

### Task 1: Create Workflow Service and Seed Command

**Covers:** [S1]

**Files:**
- Create: `backend/apps/workflows/services/__init__.py`
- Create: `backend/apps/workflows/services/workflow_service.py`
- Create: `backend/apps/workflows/management/__init__.py`
- Create: `backend/apps/workflows/management/commands/__init__.py`
- Create: `backend/apps/workflows/management/commands/seed_workflows.py`

- [x]**Step 1: Create services package and WorkflowService**

```python
# backend/apps/workflows/services/workflow_service.py
"""Workflow engine service: seed, start, advance, and task assignment."""
import datetime
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from apps.workflows.models import Workflow, WorkflowStep, WorkflowInstance, Task
from apps.workflows.workflow_definitions import ALL_WORKFLOWS, get_workflow_steps

User = get_user_model()

WORKFLOW_TYPE_TO_STEP_TYPE = {
    'APPROVAL': 'APPROVAL',
    'REVIEW': 'REVIEW',
    'NOTIFICATION': 'NOTIFICATION',
    'ROUTING': 'ROUTING',
}


class WorkflowService:
    """Creates, starts, and advances workflow instances from configured definitions."""

    @staticmethod
    def seed_all(*, created_by, overwrite=False) -> dict:
        """Create Workflow + WorkflowStep rows from ALL_WORKFLOWS definitions."""
        if created_by is None:
            created_by = User.objects.filter(role='SYSADMIN').order_by('id').first()
        if created_by is None:
            raise ValidationError('No SYSADMIN user available to own seeded workflows.')

        stats = {'created': 0, 'updated': 0}
        for wf_type, definition in ALL_WORKFLOWS.items():
            workflow, created = Workflow.objects.get_or_create(
                name=definition['name'],
                defaults={
                    'description': definition['description'],
                    'created_by': created_by,
                    'status': 'ACTIVE',
                    'is_template': True,
                    'trigger_config': {'workflow_type': wf_type},
                },
            )
            if not created and overwrite:
                workflow.description = definition['description']
                workflow.save(update_fields=['description'])
            if created:
                stats['created'] += 1
            else:
                stats['updated'] += 1

            existing = {s.order: s for s in workflow.steps.all()}
            for step_def in get_workflow_steps(wf_type):
                step_type = 'ROUTING'
                if step_def.get('action') in ('APPROVED', 'FINAL_APPROVAL', 'TG_APPROVAL', 'DEPT_HEAD_APPROVAL', 'APPROVAL'):
                    step_type = 'APPROVAL'
                step, step_created = WorkflowStep.objects.get_or_create(
                    workflow=workflow,
                    order=step_def['order'],
                    defaults={
                        'name': step_def['name'],
                        'description': step_def['description'],
                        'step_type': step_type,
                        'assigned_role': step_def.get('required_role', ''),
                        'is_required': True,
                    },
                )
                if not step_created:
                    continue
            if not created:
                stats['updated'] += 1

        return stats

    @staticmethod
    def get_workflow_by_type(workflow_type):
        return Workflow.objects.filter(
            trigger_config__workflow_type=workflow_type, status='ACTIVE'
        ).first()

    @staticmethod
    @transaction.atomic
    def start_instance(*, workflow_type, initiated_by, reference_number, data=None) -> WorkflowInstance:
        """Create a WorkflowInstance for a workflow type and assign its first task."""
        workflow = WorkflowService.get_workflow_by_type(workflow_type)
        if workflow is None:
            raise ValidationError(f'No active workflow found for type: {workflow_type}')

        instance = WorkflowInstance.objects.create(
            workflow=workflow,
            initiated_by=initiated_by,
            reference_number=reference_number,
            status='PENDING',
            data=data or {},
        )

        first_step = workflow.steps.order_by('order').first()
        if first_step:
            instance.current_step = first_step
            instance.status = 'IN_PROGRESS'
            instance.save(update_fields=['current_step', 'status', 'updated_at'])
            WorkflowService._assign_task(instance, first_step)

        return instance

    @staticmethod
    @transaction.atomic
    def advance(instance, *, user, decision='APPROVE', comments='') -> dict:
        """Complete the current task and move to the next step (or complete the workflow)."""
        if instance.status in ('COMPLETED', 'CANCELLED'):
            raise ValidationError(f'Workflow is already {instance.status}.')

        if instance.current_step is None:
            raise ValidationError('Workflow has no current step.')

        current_task = Task.objects.filter(
            workflow_instance=instance,
            step=instance.current_step,
            status__in=['PENDING', 'IN_PROGRESS'],
        ).order_by('id').first()

        if current_task and current_task.assigned_to != user and user.role not in ('SYSADMIN',):
            if instance.current_step.assigned_role and user.role != instance.current_step.assigned_role:
                raise ValidationError(
                    f'User {user} cannot act at step {instance.current_step.name}.'
                )

        if current_task:
            current_task.status = 'COMPLETED'
            current_task.decision = decision
            current_task.comments = comments
            current_task.completed_at = timezone.now()
            current_task.save(update_fields=['status', 'decision', 'comments', 'completed_at'])

        next_step = instance.workflow.steps.filter(order__gt=instance.current_step.order).order_by('order').first()

        if next_step is None:
            instance.status = 'COMPLETED'
            instance.current_step = None
            instance.completed_at = timezone.now()
            instance.save(update_fields=['status', 'current_step', 'completed_at', 'updated_at'])
            return {'status': 'COMPLETED', 'instance_id': instance.id}

        instance.current_step = next_step
        instance.status = 'IN_PROGRESS'
        instance.save(update_fields=['current_step', 'status', 'updated_at'])
        WorkflowService._assign_task(instance, next_step)
        return {'status': 'IN_PROGRESS', 'instance_id': instance.id, 'next_step': next_step.name}

    @staticmethod
    def _assign_task(instance, step):
        """Assign a task for the given step to a matching-role user (or SYSADMIN)."""
        assignee = None
        if step.assigned_role:
            assignee = User.objects.filter(role=step.assigned_role, is_active=True).order_by('id').first()
        if assignee is None:
            assignee = User.objects.filter(role='SYSADMIN', is_active=True).order_by('id').first()
        if assignee is None:
            assignee = instance.initiated_by

        return Task.objects.create(
            workflow_instance=instance,
            step=step,
            assigned_to=assignee,
            status='PENDING',
        )
```

- [x]**Step 2: Create seed_workflows management command**

```python
# backend/apps/workflows/management/commands/seed_workflows.py
from django.core.management.base import BaseCommand
from apps.workflows.services.workflow_service import WorkflowService


class Command(BaseCommand):
    help = 'Seed all configured workflow definitions into Workflow/WorkflowStep models'

    def add_arguments(self, parser):
        parser.add_argument('--overwrite', action='store_true', help='Update existing workflow descriptions')

    def handle(self, *args, **options):
        stats = WorkflowService.seed_all(created_by=None, overwrite=options['overwrite'])
        self.stdout.write(self.style.SUCCESS(
            f'Workflows seeded: {stats["created"]} created, {stats["updated"]} updated'
        ))
```

- [x]**Step 3: Write service tests**

Create `backend/apps/workflows/tests/test_workflow_service.py` covering: seed_all idempotency, start_instance assigns first task, advance completes workflow at last step, advance rejects wrong-role user, reference_number uniqueness.

- [x]**Step 4: Run tests**

Run: `$env:DJANGO_SETTINGS_MODULE='config.settings.test'; $env:DJANGO_SECRET_KEY='ci-test-secret-key-not-for-production'; cd C:\educationdistrictivportal\backend; python manage.py test apps.workflows -v1`

Expected: All PASS

- [x]**Step 5: Commit**

```bash
git add backend/apps/workflows/services backend/apps/workflows/management backend/apps/workflows/tests
git commit -m "feat(workflows): add WorkflowService engine, seed command, and service tests"
```

---

### Task 2: Wire Workflow Engine into Viewsets

**Covers:** [S1]

**Files:**
- Modify: `backend/apps/workflows/views.py`
- Modify: `backend/apps/workflows/serializers.py`

- [x]**Step 1: Add start/advance/cancel actions to WorkflowInstanceViewSet**

```python
# In workflows/views.py add to WorkflowInstanceViewSet:
    @action(detail=False, methods=['post'])
    def start(self, request):
        workflow_type = request.data.get('workflow_type')
        reference_number = request.data.get('reference_number')
        if not workflow_type or not reference_number:
            return Response({'error': 'workflow_type and reference_number are required.'}, status=400)
        instance = WorkflowService.start_instance(
            workflow_type=workflow_type,
            initiated_by=request.user,
            reference_number=reference_number,
            data=request.data.get('data'),
        )
        return Response(WorkflowInstanceSerializer(instance).data, status=201)

    @action(detail=True, methods=['post'])
    def advance(self, request, pk=None):
        instance = self.get_object()
        try:
            result = WorkflowService.advance(
                instance, user=request.user,
                decision=request.data.get('decision', 'APPROVE'),
                comments=request.data.get('comments', ''),
            )
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)
        return Response(result)
```

- [x]**Step 2: Run tests and verify endpoints work**

Run: `$env:DJANGO_SETTINGS_MODULE='config.settings.test'; $env:DJANGO_SECRET_KEY='ci-test-secret-key-not-for-production'; cd C:\educationdistrictivportal\backend; python manage.py test apps.workflows -v1`

Expected: All PASS (including new API-action tests)

- [x]**Step 3: Commit**

```bash
git add backend/apps/workflows/views.py backend/apps/workflows/tests
git commit -m "feat(workflows): expose start/advance workflow actions in API"
```

---

### Task 3: Add Registry Memo Approval/Circulation Viewsets

**Covers:** [S2]

**Files:**
- Modify: `backend/apps/registry/views.py`
- Modify: `backend/apps/registry/urls.py`
- Modify: `backend/apps/registry/admin.py`

- [x]**Step 1: Add MemoApprovalViewSet and MemoCirculationViewSet**

```python
# registry/views.py
class MemoApprovalViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MemoApproval.objects.select_related('memo_workflow', 'approver').all()
    serializer_class = MemoApprovalSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['memo_workflow', 'approver', 'status']


class MemoCirculationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MemoCirculation.objects.select_related('memo_workflow', 'recipient').all()
    serializer_class = MemoCirculationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['memo_workflow', 'recipient', 'status']
```

- [x]**Step 2: Register routes**

```python
# registry/urls.py
router.register('memo-approvals', MemoApprovalViewSet)
router.register('memo-circulations', MemoCirculationViewSet)
```

- [x]**Step 3: Register in admin**

```python
# registry/admin.py - add MemoApproval, MemoCirculation admin classes
```

- [x]**Step 4: Write API tests**

Create `backend/apps/registry/tests/test_memo_workflow_api.py` covering: create memo → submit → approve → circulate → acknowledge → archive full flow, memo approval list endpoint, memo circulation list endpoint.

- [x]**Step 5: Run tests**

Run: `$env:DJANGO_SETTINGS_MODULE='config.settings.test'; $env:DJANGO_SECRET_KEY='ci-test-secret-key-not-for-production'; cd C:\educationdistrictivportal\backend; python manage.py test apps.registry -v1`

Expected: All PASS

- [x]**Step 6: Commit**

```bash
git add backend/apps/registry/views.py backend/apps/registry/urls.py backend/apps/registry/admin.py backend/apps/registry/tests
git commit -m "feat(registry): add memo approval/circulation viewsets, routes, admin, and full-flow tests"
```

---

### Task 4: Add Mail Workflow Movement Viewsets

**Covers:** [S3]

**Files:**
- Modify: `backend/apps/mail_workflow/views.py`
- Modify: `backend/apps/mail_workflow/urls.py`
- Modify: `backend/apps/mail_workflow/admin.py`

- [x]**Step 1: Add movement viewsets**

```python
# mail_workflow/views.py - all read-only, role-scoped
class MailMovementViewSet(viewsets.ReadOnlyModelViewSet): ...
class OutgoingMailMovementViewSet(viewsets.ReadOnlyModelViewSet): ...
class SchoolHQCorrespondenceMovementViewSet(viewsets.ReadOnlyModelViewSet): ...
class MailCorrespondenceMovementViewSet(viewsets.ReadOnlyModelViewSet): ...
```

- [x]**Step 2: Register routes**

```python
# mail_workflow/urls.py
router.register('incoming-movements', MailMovementViewSet, basename='mailmovement')
router.register('outgoing-movements', OutgoingMailMovementViewSet, basename='outgoingmailmovement')
router.register('school-hq-movements', SchoolHQCorrespondenceMovementViewSet, basename='schoolhqmovement')
router.register('correspondence-movements', MailCorrespondenceMovementViewSet, basename='mailcorrespondencemovement')
```

- [x]**Step 3: Register in admin** (all movement + approval models)

- [x]**Step 4: Write API tests**

Create `backend/apps/mail_workflow/tests/test_movement_api.py` covering: incoming mail movement history after forward/assign, outgoing movement after dispatch, movement list endpoints role-scoping.

- [x]**Step 5: Run tests**

Run: `$env:DJANGO_SETTINGS_MODULE='config.settings.test'; $env:DJANGO_SECRET_KEY='ci-test-secret-key-not-for-production'; cd C:\educationdistrictivportal\backend; python manage.py test apps.mail_workflow -v1`

Expected: All PASS

- [x]**Step 6: Commit**

```bash
git add backend/apps/mail_workflow/views.py backend/apps/mail_workflow/urls.py backend/apps/mail_workflow/admin.py backend/apps/mail_workflow/tests
git commit -m "feat(mail_workflow): add movement viewsets, routes, admin, and tests"
```

---

### Task 5: Final Verification

**Covers:** [S4]

**Files:** None (verification only)

- [x]**Step 1: Run full test suite**

Run: `$env:DJANGO_SETTINGS_MODULE='config.settings.test'; $env:DJANGO_SECRET_KEY='ci-test-secret-key-not-for-production'; cd C:\educationdistrictivportal\backend; python manage.py test apps.workflows apps.registry apps.mail_workflow -v1`

Expected: ALL PASS

- [x]**Step 2: Verify migrations clean**

Run: `$env:DJANGO_SETTINGS_MODULE='config.settings.local'; $env:DJANGO_SECRET_KEY='ci-test-secret-key-not-for-production'; cd C:\educationdistrictivportal\backend; python manage.py makemigrations --check`

Expected: No changes detected

- [x]**Step 3: Verify seed command**

Run: `$env:DJANGO_SETTINGS_MODULE='config.settings.local'; $env:DJANGO_SECRET_KEY='ci-test-secret-key-not-for-production'; cd C:\educationdistrictivportal\backend; python manage.py seed_workflows`

Expected: 7 workflows created (7 created, 0 updated on first run; 0/7 on second)

- [x]**Step 4: Update plan checkboxes and commit plan**

```bash
git add docs/compose/plans/2026-08-09-e-registry-mail-workflow-automation.md
git commit -m "docs: add E-Registry + Mail Workflow automation plan"
```
