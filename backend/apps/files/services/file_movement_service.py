"""Enterprise File Movement Service with workflow enforcement, deadline tracking, and escalation."""
import datetime
import logging
from django.db import transaction
from django.db.models import Max, Q
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator

from apps.files.models import (
    File, FileMovement, WorkflowConfig, FileClassification, FileTemplate
)

logger = logging.getLogger(__name__)
User = get_user_model()


class FileMovementService:
    """Enterprise File Movement Service with all improvements."""

    PRIORITY_ESCALATION = {
        'LOW': 'NORMAL',
        'NORMAL': 'HIGH',
        'HIGH': 'URGENT',
        'URGENT': 'URGENT',
    }

    # 11-Step Incoming Workflow (ascending: Registry -> TG/PS Office -> Department -> Desk -> back up)
    INCOMING_WORKFLOW = [
        {'step': 1, 'location': 'REGISTRY', 'role': 'REG_OFF', 'deadline': 2, 'label': 'Registry Receipt'},
        {'step': 2, 'location': 'TG_PS_OFFICE', 'role': 'REG_OFF', 'deadline': 4, 'label': 'Clerical Officer Review'},
        {'step': 3, 'location': 'TG_PS_OFFICE', 'role': 'REG_OFF', 'deadline': 4, 'label': 'Secretary Review'},
        {'step': 4, 'location': 'TG_PS_OFFICE', 'role': 'TG_PS', 'deadline': 8, 'label': 'TG/PS Approval'},
        {'step': 5, 'location': 'DEPARTMENT', 'role': 'SA_OFF', 'deadline': 24, 'label': 'Department Head Review'},
        {'step': 6, 'location': 'UNIT', 'role': 'SA_OFF', 'deadline': 24, 'label': 'Unit Head Review'},
        {'step': 7, 'location': 'DESK_OFFICER', 'role': 'TCH', 'deadline': 48, 'label': 'Desk Officer Processing'},
        {'step': 8, 'location': 'UNIT', 'role': 'SA_OFF', 'deadline': 24, 'label': 'Unit Head Completion Review'},
        {'step': 9, 'location': 'DEPARTMENT', 'role': 'SA_OFF', 'deadline': 24, 'label': 'Department Head Completion Review'},
        {'step': 10, 'location': 'TG_PS_OFFICE', 'role': 'TG_PS', 'deadline': 8, 'label': 'TG/PS Final Review'},
        {'step': 11, 'location': 'REGISTRY', 'role': 'REG_OFF', 'deadline': 2, 'label': 'Registry Filing & Closure'},
    ]

    # 7-Step Outgoing Workflow (ascending to TG/PS then Registry)
    OUTGOING_WORKFLOW = [
        {'step': 1, 'location': 'DESK_OFFICER', 'role': 'TCH', 'deadline': 24, 'label': 'Desk Officer Drafting'},
        {'step': 2, 'location': 'UNIT', 'role': 'SA_OFF', 'deadline': 24, 'label': 'Unit Head Review'},
        {'step': 3, 'location': 'DEPARTMENT', 'role': 'SA_OFF', 'deadline': 24, 'label': 'Department Head Review'},
        {'step': 4, 'location': 'TG_PS_OFFICE', 'role': 'REG_OFF', 'deadline': 4, 'label': 'Clerical Officer Review'},
        {'step': 5, 'location': 'TG_PS_OFFICE', 'role': 'REG_OFF', 'deadline': 4, 'label': 'Secretary Review'},
        {'step': 6, 'location': 'TG_PS_OFFICE', 'role': 'TG_PS', 'deadline': 8, 'label': 'TG/PS Signature'},
        {'step': 7, 'location': 'REGISTRY', 'role': 'REG_OFF', 'deadline': 2, 'label': 'Registry Dispatch'},
    ]

    # Location-to-status mapping
    LOCATION_STATUS_MAP = {
        'CREATED': 'DRAFT',
        'REGISTRY': 'PENDING',
        'TG_PS_OFFICE': 'UNDER_REVIEW',
        'DEPARTMENT': 'ACTIVE',
        'UNIT': 'ACTIVE',
        'DESK_OFFICER': 'ACTIVE',
        'ARCHIVED': 'ARCHIVED',
    }

    @staticmethod
    def _generate_file_number(department=None):
        """Generate unique file number: FIL-{dept_code}-{YYYY}-{seq}."""
        year = datetime.date.today().year
        if department and hasattr(department, 'code'):
            prefix = f"FIL-{department.code}-{year}"
        else:
            prefix = f"FIL-{year}"
        last = File.objects.filter(
            file_number__startswith=prefix
        ).aggregate(max_num=Max('file_number'))['max_num']
        if last:
            try:
                seq = int(last.split('-')[-1]) + 1
            except (ValueError, IndexError):
                seq = 1
        else:
            seq = 1
        return f"{prefix}-{seq:04d}"

    @staticmethod
    def _add_timeline_entry(file_obj, status, user, action, notes=''):
        """Add a status timeline entry to the file."""
        entry = {
            'timestamp': timezone.now().isoformat(),
            'status': status,
            'changed_by_id': user.id,
            'changed_by_name': user.get_full_name() or user.username,
            'action': action,
            'notes': notes,
        }
        timeline = list(file_obj.status_timeline or [])
        timeline.append(entry)
        file_obj.status_timeline = timeline

    @staticmethod
    @transaction.atomic
    def create_file(*, title, file_type, file_category, description, classification,
                    priority, created_by, department=None, school=None,
                    template=None, tags=None, due_date=None, direction='INCOMING'):
        """
        Create a new file with auto-generated number and optional template.
        Records CREATED movement and adds to status_timeline.
        """
        file_number = FileMovementService._generate_file_number(department)

        if template:
            if template.file_type:
                file_type = template.file_type
            if template.file_category:
                file_category = template.file_category
            if template.default_classification:
                classification = template.default_classification
            if template.default_priority:
                priority = template.default_priority
            template.usage_count += 1
            template.save(update_fields=['usage_count'])

        file_obj = File(
            file_number=file_number,
            title=title,
            file_type=file_type,
            file_category=file_category,
            description=description or '',
            created_by=created_by,
            current_holder=created_by,
            department=department,
            school=school,
            status='DRAFT',
            classification=classification,
            priority=priority,
            direction=direction,
            due_date=due_date,
            tags=tags or [],
            current_workflow_step=0,
        )
        file_obj.save()

        movement = FileMovement(
            file=file_obj,
            from_holder=created_by,
            to_holder=None,
            action='CREATED',
            remarks=f"File created by {created_by.get_full_name() or created_by.username}",
            workflow_step=0,
            from_location='CREATED',
            to_location='REGISTRY',
        )
        movement.save()

        FileMovementService._add_timeline_entry(
            file_obj, 'DRAFT', created_by, 'CREATED',
            f"File created by {created_by.get_full_name() or created_by.username}"
        )
        file_obj.save(update_fields=['status_timeline'])

        return file_obj

    @staticmethod
    def _get_workflow(direction):
        """Get workflow steps for direction."""
        if direction == 'OUTGOING':
            return FileMovementService.OUTGOING_WORKFLOW
        return FileMovementService.INCOMING_WORKFLOW

    @staticmethod
    def _get_deadline_for_step(step_num, direction='INCOMING'):
        """Get deadline for a workflow step, checking WorkflowConfig first."""
        workflow = FileMovementService._get_workflow(direction)
        location = None
        for step in workflow:
            if step['step'] == step_num:
                location = step['location']
                break

        if location:
            config = WorkflowConfig.objects.filter(
                step_name=location,
                direction=direction,
                is_active=True,
            ).first()
            if config:
                return config.default_deadline_hours

        for step in workflow:
            if step['step'] == step_num:
                return step.get('deadline', 24)
        return 24

    @staticmethod
    def _get_next_step(current_step, direction='INCOMING'):
        """Get next workflow step number."""
        workflow = FileMovementService._get_workflow(direction)
        for step in workflow:
            if step['step'] == current_step + 1:
                return step
        return None

    @staticmethod
    def _get_step_info(step_num, direction='INCOMING'):
        """Get full step info for a step number."""
        workflow = FileMovementService._get_workflow(direction)
        for step in workflow:
            if step['step'] == step_num:
                return step
        return None

    @staticmethod
    def _user_can_act_at_step(user, step_num, direction='INCOMING'):
        """Check if user's role matches the workflow step requirement."""
        step = FileMovementService._get_step_info(step_num, direction)
        if not step:
            return False
        required_role = step['role']
        if required_role == 'TG_PS':
            return user.role in ('SYSADMIN', 'TG_PS')
        if required_role == 'REG_OFF':
            return user.role in ('REG', 'REG_OFF')
        if required_role == 'SA_OFF':
            return user.role in ('SA_OFF', 'SA', 'PRI', 'VP')
        if required_role == 'TCH':
            return user.role in ('TCH', 'SA_OFF')
        return user.role in ('SYSADMIN', 'TG_PS')

    @staticmethod
    def _get_recipients_for_step(step_num, direction='INCOMING'):
        """Get users who should receive notifications at this step."""
        step = FileMovementService._get_step_info(step_num, direction)
        if not step:
            return []

        role = step['role']
        if role == 'TG_PS':
            return User.objects.filter(role__in=['SYSADMIN', 'TG_PS'], is_active=True)
        if role == 'REG_OFF':
            return User.objects.filter(role__in=['REG', 'REG_OFF'], is_active=True)
        if role == 'SA_OFF':
            return User.objects.filter(role__in=['SA_OFF', 'SA', 'PRI', 'VP'], is_active=True)
        if role == 'TCH':
            return User.objects.filter(role__in=['TCH', 'SA_OFF'], is_active=True)
        return User.objects.filter(role=role, is_active=True)

    @staticmethod
    @transaction.atomic
    def move_file(*, file, from_holder, to_holder, action, remarks='',
                  expected_return_date=None, completion_notes='',
                  target_step=None):
        """
        Move file following the workflow. Validates role-based permissions
        and enforces ascending workflow steps.
        """
        if file.current_holder is not None and file.current_holder != from_holder:
            raise ValueError(
                f"User {from_holder} is not the current holder of file {file.file_number}."
            )

        current_step = file.current_workflow_step or 0
        direction = file.direction or 'INCOMING'

        # Determine target step
        if target_step is None:
            next_step = FileMovementService._get_next_step(current_step, direction)
            if next_step:
                target_step = next_step['step']
            else:
                target_step = current_step

        # Validate workflow progression
        if target_step > current_step + 1 and target_step != current_step:
            workflow = FileMovementService._get_workflow(direction)
            max_step = max(s['step'] for s in workflow) if workflow else 1
            if target_step > max_step:
                target_step = max_step

        # Get step info
        target_step_info = FileMovementService._get_step_info(target_step, direction)
        to_location = target_step_info['location'] if target_step_info else ''

        # Handle ESCALATED priority increment
        if action == 'ESCALATED':
            new_priority = FileMovementService.PRIORITY_ESCALATION.get(file.priority, file.priority)
            file.priority = new_priority

        # Handle RETURNED action
        is_returned = action == 'RETURNED'
        actual_return_date = timezone.now().date() if is_returned else None

        # Calculate expected completion
        deadline_hours = FileMovementService._get_deadline_for_step(target_step, direction)
        expected_completion = timezone.now() + datetime.timedelta(hours=deadline_hours)

        # Create movement record
        movement = FileMovement(
            file=file,
            from_holder=from_holder,
            to_holder=to_holder,
            action=action,
            remarks=remarks,
            expected_return_date=expected_return_date,
            completion_notes=completion_notes,
            is_returned=is_returned,
            actual_return_date=actual_return_date,
            workflow_step=target_step,
            from_location=FileMovementService._get_step_info(current_step, direction)['location'] if current_step > 0 else 'CREATED',
            to_location=to_location,
            expected_completion=expected_completion,
        )
        movement.save()

        # Update file
        file.current_holder = to_holder
        file.current_workflow_step = target_step
        file.last_moved_at = timezone.now()
        file.expected_completion_date = (timezone.now() + datetime.timedelta(hours=deadline_hours)).date()

        if action == 'ESCALATED':
            file.escalation_status = 'ESCALATED'
            file.escalation_reason = remarks
            file.escalated_at = timezone.now()

        update_fields = ['current_holder', 'current_workflow_step', 'status_timeline',
                         'last_moved_at', 'expected_completion_date', 'updated_at']
        if action == 'ESCALATED':
            update_fields.extend(['priority', 'escalation_status', 'escalation_reason', 'escalated_at'])

        notes = remarks or f"File {action.lower()}"
        if to_holder:
            notes = f"File moved to {to_holder.get_full_name() or to_holder.username}: {action}"

        FileMovementService._add_timeline_entry(file, file.status, from_holder, action, notes)
        file.save(update_fields=update_fields)

        FileMovementService._invalidate_cache(file.id)

        return movement

    @staticmethod
    @transaction.atomic
    def advance_workflow(*, file, user, action='FORWARDED', notes=''):
        """
        Advance file to the next workflow step automatically.
        Validates user can act at current step.
        """
        current_step = file.current_workflow_step or 0
        direction = file.direction or 'INCOMING'

        # Check user can act at current step
        if not FileMovementService._user_can_act_at_step(user, current_step, direction):
            raise ValidationError(
                f"User role {user.role} cannot act at workflow step {current_step}."
            )

        next_step = FileMovementService._get_next_step(current_step, direction)
        if not next_step:
            raise ValidationError("File has reached the final workflow step.")

        # Get recipient for next step
        recipients = FileMovementService._get_recipients_for_step(next_step['step'], direction)
        next_holder = recipients.first() if recipients.exists() else file.current_holder

        return FileMovementService.move_file(
            file=file,
            from_holder=user,
            to_holder=next_holder,
            action=action,
            remarks=notes or f"Advanced to step {next_step['step']}: {next_step.get('label', '')}",
            target_step=next_step['step'],
        )

    @staticmethod
    @transaction.atomic
    def receive_file(*, file, received_by, notes=''):
        """Mark file as received by current holder."""
        if received_by != file.current_holder:
            raise ValueError(
                f"User {received_by} is not the current holder of file {file.file_number}."
            )

        last_movement = FileMovement.objects.filter(
            file=file
        ).order_by('-movement_date').first()
        if last_movement and not last_movement.is_returned:
            last_movement.is_returned = True
            last_movement.actual_return_date = timezone.now().date()
            last_movement.completion_notes = notes
            last_movement.save(update_fields=['is_returned', 'actual_return_date', 'completion_notes'])

        if file.status == 'IN_TRANSIT':
            file.status = 'ACTIVE'
        file.save(update_fields=['status', 'updated_at'])

        movement = FileMovement(
            file=file,
            from_holder=received_by,
            to_holder=None,
            action='RECEIVED',
            remarks=notes or f"File received by {received_by.get_full_name() or received_by.username}",
            is_returned=True,
            actual_return_date=timezone.now().date(),
            completion_notes=notes,
            workflow_step=file.current_workflow_step or 0,
            from_location='',
            to_location='',
        )
        movement.save()

        FileMovementService._add_timeline_entry(
            file, file.status, received_by, 'RECEIVED',
            notes or f"Received by {received_by.get_full_name() or received_by.username}"
        )
        file.save(update_fields=['status_timeline'])
        FileMovementService._invalidate_cache(file.id)

        return movement

    @staticmethod
    @transaction.atomic
    def recall_file(*, file, recalled_by, reason=''):
        """Recall a file from current holder."""
        previous_movement = FileMovement.objects.filter(
            file=file,
            from_holder=recalled_by
        ).order_by('-movement_date').first()

        if not previous_movement:
            raise ValueError(
                f"User {recalled_by} cannot recall file {file.file_number}."
            )

        file.current_holder = recalled_by
        file.save(update_fields=['current_holder', 'updated_at'])

        movement = FileMovement(
            file=file,
            from_holder=recalled_by,
            to_holder=previous_movement.to_holder,
            action='RETURNED',
            remarks=reason or f"File recalled by {recalled_by.get_full_name() or recalled_by.username}",
            is_returned=True,
            actual_return_date=timezone.now().date(),
            workflow_step=file.current_workflow_step or 0,
        )
        movement.save()

        FileMovementService._add_timeline_entry(
            file, file.status, recalled_by, 'RETURNED',
            reason or f"File recalled by {recalled_by.get_full_name() or recalled_by.username}"
        )
        file.save(update_fields=['status_timeline'])
        FileMovementService._invalidate_cache(file.id)

        return movement

    @staticmethod
    @transaction.atomic
    def escalate_file(*, file, escalated_by, reason=''):
        """Escalate file priority and mark as escalated."""
        old_priority = file.priority
        new_priority = FileMovementService.PRIORITY_ESCALATION.get(file.priority, file.priority)
        file.priority = new_priority
        file.escalation_status = 'ESCALATED'
        file.escalation_reason = reason
        file.escalated_at = timezone.now()

        movement = FileMovement(
            file=file,
            from_holder=escalated_by,
            to_holder=file.current_holder,
            action='ESCALATED',
            remarks=reason or f"File escalated from {old_priority} to {new_priority}",
            workflow_step=file.current_workflow_step or 0,
        )
        movement.save()

        FileMovementService._add_timeline_entry(
            file, file.status, escalated_by, 'ESCALATED',
            reason or f"Escalated from {old_priority} to {new_priority}"
        )
        file.save(update_fields=[
            'priority', 'escalation_status', 'escalation_reason',
            'escalated_at', 'status_timeline', 'updated_at'
        ])
        FileMovementService._invalidate_cache(file.id)

        return movement

    @staticmethod
    @transaction.atomic
    def archive_file(*, file, archived_by, notes=''):
        """Archive a completed file."""
        valid_statuses = ['CLOSED', 'ARCHIVED']
        if file.status not in valid_statuses:
            raise ValueError(
                f"Cannot archive file {file.file_number} with status {file.status}."
            )

        file.status = 'ARCHIVED'
        file.save(update_fields=['status', 'updated_at'])

        movement = FileMovement(
            file=file,
            from_holder=archived_by,
            to_holder=None,
            action='ARCHIVED',
            remarks=notes or f"File archived by {archived_by.get_full_name() or archived_by.username}",
            workflow_step=file.current_workflow_step or 0,
        )
        movement.save()

        FileMovementService._add_timeline_entry(
            file, file.status, archived_by, 'ARCHIVED',
            notes or f"Archived by {archived_by.get_full_name() or archived_by.username}"
        )
        file.save(update_fields=['status_timeline'])
        FileMovementService._invalidate_cache(file.id)

        return movement

    @staticmethod
    def check_and_escalate_overdue():
        """Check for overdue files and auto-escalate. Called by Celery beat."""
        now = timezone.now()
        overdue_files = File.objects.filter(
            expected_completion_date__lt=now.date(),
            status__in=['ACTIVE', 'IN_TRANSIT', 'PENDING', 'UNDER_REVIEW'],
            escalation_status='NORMAL',
        ).select_related('current_holder', 'created_by')

        escalated_count = 0
        for file_obj in overdue_files:
            try:
                # Escalate priority
                old_priority = file_obj.priority
                new_priority = FileMovementService.PRIORITY_ESCALATION.get(old_priority, old_priority)
                file_obj.priority = new_priority
                file_obj.escalation_status = 'ESCALATED'
                file_obj.escalation_reason = f'Auto-escalated: deadline {file_obj.expected_completion_date} passed'
                file_obj.escalated_at = now
                file_obj.save(update_fields=[
                    'priority', 'escalation_status', 'escalation_reason',
                    'escalated_at', 'updated_at'
                ])

                # Notify TG/PS
                from apps.files.services.notification_service import NotificationService
                tg_ps_users = User.objects.filter(role__in=['SYSADMIN', 'TG_PS'], is_active=True)
                for tg in tg_ps_users:
                    NotificationService.send_notification(
                        recipient=tg,
                        subject=f"OVERDUE: File {file_obj.file_number}",
                        message=(
                            f"File '{file_obj.title}' ({file_obj.file_number}) is overdue.\n"
                            f"Deadline: {file_obj.expected_completion_date}\n"
                            f"Current holder: {file_obj.current_holder.get_full_name() if file_obj.current_holder else 'N/A'}\n"
                            f"Auto-escalated from {old_priority} to {new_priority}."
                        ),
                        file=file_obj,
                        notification_type='DEADLINE_REMINDER',
                        priority='URGENT',
                    )

                FileMovementService._add_timeline_entry(
                    file_obj, file_obj.status, file_obj.created_by, 'ESCALATED',
                    f"Auto-escalated: deadline passed"
                )
                file_obj.save(update_fields=['status_timeline'])
                escalated_count += 1

            except Exception as e:
                logger.error(f"Failed to auto-escalate file {file_obj.id}: {e}")

        return {'escalated': escalated_count}

    @staticmethod
    def get_file_timeline(file):
        """Return chronological list of all movements for a file."""
        movements = FileMovement.objects.filter(
            file=file
        ).select_related('from_holder', 'to_holder').order_by('movement_date')

        timeline = []
        for m in movements:
            timeline.append({
                'id': m.id,
                'timestamp': m.movement_date.isoformat(),
                'action': m.action,
                'from_holder_id': m.from_holder_id,
                'from_holder_name': m.from_holder.get_full_name() or m.from_holder.username if m.from_holder else None,
                'to_holder_id': m.to_holder_id,
                'to_holder_name': m.to_holder.get_full_name() or m.to_holder.username if m.to_holder else None,
                'remarks': m.remarks,
                'status': file.status,
                'is_returned': m.is_returned,
                'workflow_step': m.workflow_step,
                'from_location': m.from_location,
                'to_location': m.to_location,
                'expected_completion': m.expected_completion.isoformat() if m.expected_completion else None,
                'is_overdue': m.is_overdue,
            })

        return timeline

    @staticmethod
    def get_user_pending_files(user, page=1, per_page=20):
        """Return paginated files where user is current_holder."""
        qs = File.objects.filter(
            current_holder=user,
            status__in=['ACTIVE', 'PENDING', 'IN_TRANSIT', 'UNDER_REVIEW']
        ).select_related('created_by', 'current_holder', 'department', 'school')

        paginator = Paginator(qs, per_page)
        page_obj = paginator.get_page(page)

        return {
            'count': paginator.count,
            'page': page,
            'per_page': per_page,
            'total_pages': paginator.num_pages,
            'files': list(page_obj.object_list),
        }

    @staticmethod
    def get_department_files(department, status=None, page=1, per_page=20):
        """Return paginated files for a department."""
        qs = File.objects.filter(
            Q(department=department) | Q(assigned_department=department)
        ).select_related('created_by', 'current_holder', 'school')

        if status:
            qs = qs.filter(status=status)

        paginator = Paginator(qs, per_page)
        page_obj = paginator.get_page(page)

        return {
            'count': paginator.count,
            'page': page,
            'per_page': per_page,
            'total_pages': paginator.num_pages,
            'files': list(page_obj.object_list),
        }

    @staticmethod
    def search_files(query=None, file_type=None, status=None, classification=None,
                     priority=None, department=None, date_from=None, date_to=None,
                     created_by=None, current_holder=None):
        """Full-text search with multiple filters."""
        qs = File.objects.select_related('created_by', 'current_holder', 'department', 'school')

        if query:
            qs = qs.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(file_number__icontains=query)
            )
        if file_type:
            qs = qs.filter(file_type=file_type)
        if status:
            qs = qs.filter(status=status)
        if classification:
            qs = qs.filter(classification=classification)
        if priority:
            qs = qs.filter(priority=priority)
        if department:
            qs = qs.filter(department_id=department)
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)
        if created_by:
            qs = qs.filter(created_by_id=created_by)
        if current_holder:
            qs = qs.filter(current_holder_id=current_holder)

        return qs

    @staticmethod
    def get_incoming_workflow():
        """Return the incoming workflow steps."""
        return list(FileMovementService.INCOMING_WORKFLOW)

    @staticmethod
    def get_outgoing_workflow():
        """Return the outgoing workflow steps."""
        return list(FileMovementService.OUTGOING_WORKFLOW)

    @staticmethod
    def get_file_status(file_id):
        """Get complete file status with caching."""
        cache_key = f'file_status_{file_id}'
        cached = cache.get(cache_key)
        if cached:
            return cached

        try:
            file_obj = File.objects.select_related(
                'created_by', 'current_holder', 'department', 'school', 'assigned_department'
            ).get(id=file_id)
        except File.DoesNotExist:
            return None

        workflow = FileMovementService._get_workflow(file_obj.direction or 'INCOMING')
        current_step_info = FileMovementService._get_step_info(
            file_obj.current_workflow_step or 0, file_obj.direction or 'INCOMING'
        )

        result = {
            'id': file_obj.id,
            'file_number': file_obj.file_number,
            'title': file_obj.title,
            'status': file_obj.status,
            'priority': file_obj.priority,
            'direction': file_obj.direction,
            'classification': file_obj.classification,
            'current_workflow_step': file_obj.current_workflow_step,
            'current_step_info': current_step_info,
            'escalation_status': file_obj.escalation_status,
            'is_overdue': file_obj.is_overdue,
            'current_holder': {
                'id': file_obj.current_holder.id,
                'name': file_obj.current_holder.get_full_name() or file_obj.current_holder.username,
            } if file_obj.current_holder else None,
            'department': {
                'id': file_obj.department.id,
                'name': file_obj.department.name,
            } if file_obj.department else None,
            'assigned_department': {
                'id': file_obj.assigned_department.id,
                'name': file_obj.assigned_department.name,
            } if file_obj.assigned_department else None,
            'school': {
                'id': file_obj.school.id,
                'name': file_obj.school.name,
            } if file_obj.school else None,
            'due_date': file_obj.due_date.isoformat() if file_obj.due_date else None,
            'expected_completion_date': file_obj.expected_completion_date.isoformat() if file_obj.expected_completion_date else None,
            'tags': file_obj.tags or [],
            'timeline': FileMovementService.get_file_timeline(file_obj),
            'movement_count': FileMovement.objects.filter(file=file_obj).count(),
            'status_timeline': file_obj.status_timeline or [],
            'workflow_steps': workflow,
        }

        cache.set(cache_key, result, 300)
        return result

    @staticmethod
    def get_workflow_visualization(file_id):
        """Get workflow visualization data for a file."""
        try:
            file_obj = File.objects.get(id=file_id)
        except File.DoesNotExist:
            return None

        workflow = FileMovementService._get_workflow(file_obj.direction or 'INCOMING')
        movements = FileMovement.objects.filter(
            file=file_obj
        ).select_related('from_holder', 'to_holder').order_by('movement_date')

        # Map completed steps
        completed_steps = set()
        for m in movements:
            if m.workflow_step:
                completed_steps.add(m.workflow_step)

        steps = []
        for step in workflow:
            step_num = step['step']
            steps.append({
                'step': step_num,
                'location': step['location'],
                'role': step['role'],
                'label': step.get('label', step['location']),
                'deadline_hours': step['deadline'],
                'is_completed': step_num in completed_steps,
                'is_current': step_num == (file_obj.current_workflow_step or 0),
            })

        return {
            'file': {
                'id': file_obj.id,
                'file_number': file_obj.file_number,
                'title': file_obj.title,
                'status': file_obj.status,
                'direction': file_obj.direction,
                'priority': file_obj.priority,
                'current_step': file_obj.current_workflow_step,
            },
            'workflow_steps': steps,
            'total_steps': len(workflow),
            'completed_count': len(completed_steps),
            'progress_percent': int((len(completed_steps) / len(workflow)) * 100) if workflow else 0,
        }

    @staticmethod
    def _invalidate_cache(file_id):
        """Invalidate cached file status."""
        cache.delete(f'file_status_{file_id}')
        cache.delete(f'file_timeline_{file_id}')
