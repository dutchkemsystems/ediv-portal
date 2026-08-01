"""File movement service for handling file transfers and workflow operations."""
import datetime
from django.db.models import Max, Q
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from apps.files.models import (
    File, FileMovement, WorkflowConfig, FileClassification, FileTemplate
)

User = get_user_model()


class FileMovementService:
    """Service for managing file movement workflows."""

    PRIORITY_ESCALATION = {
        'LOW': 'NORMAL',
        'NORMAL': 'HIGH',
        'HIGH': 'URGENT',
        'URGENT': 'URGENT',  # Already max
    }

    @staticmethod
    def _generate_file_number(department=None):
        """Generate a unique file number in format FIL-{dept_code}-{YYYY}-{seq}."""
        year = datetime.date.today().year
        if department and hasattr(department, 'code'):
            prefix = f"FIL-{department.code}-{year}"
        else:
            prefix = f"FIL-{year}"
        last = File.objects.filter(
            file_number__startswith=prefix
        ).aggregate(max_num=Max('file_number'))['max_num']
        if last:
            seq = int(last.split('-')[-1]) + 1
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
    def create_file(*, title, file_type, file_category, description, classification,
                    priority, created_by, department=None, school=None,
                    template=None, tags=None, due_date=None):
        """
        Create a new file with auto-generated file_number.
        Format: FIL-{department_code}-{YYYY}-{sequence}
        If no department: FIL-{YYYY}-{sequence}
        If template provided, pre-fill from template defaults.
        Record CREATED movement.
        Add to status_timeline.
        """
        file_number = FileMovementService._generate_file_number(department)

        # Apply template defaults if provided
        if template:
            if template.file_type:
                file_type = template.file_type
            if template.file_category:
                file_category = template.file_category
            if template.default_classification:
                classification = template.default_classification
            if template.default_priority:
                priority = template.default_priority
            # Increment usage count
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
            due_date=due_date,
            tags=tags or [],
        )
        file_obj.save()

        # Record CREATED movement
        movement = FileMovement(
            file=file_obj,
            from_holder=created_by,
            to_holder=None,
            action='CREATED',
            remarks=f"File created by {created_by.get_full_name() or created_by.username}",
        )
        movement.save()

        # Add to status_timeline
        FileMovementService._add_timeline_entry(
            file_obj, 'DRAFT', created_by, 'CREATED',
            f"File created by {created_by.get_full_name() or created_by.username}"
        )
        file_obj.save(update_fields=['status_timeline'])

        return file_obj

    @staticmethod
    def move_file(*, file, from_holder, to_holder, action, remarks='',
                  expected_return_date=None, completion_notes=''):
        """
        Move file from one holder to another.
        Validates: from_holder must be current_holder or current_holder is None.
        Updates: file.current_holder = to_holder
        Records: FileMovement with all details
        Updates: status_timeline
        If action is RETURNED: set is_returned=True, actual_return_date=now
        If action is ESCALATED: increment priority
        """
        # Validate from_holder
        if file.current_holder is not None and file.current_holder != from_holder:
            raise ValueError(
                f"User {from_holder} is not the current holder of file {file.file_number}. "
                f"Current holder is {file.current_holder}."
            )

        # Handle ESCALATED priority increment
        if action == 'ESCALATED':
            new_priority = FileMovementService.PRIORITY_ESCALATION.get(
                file.priority, file.priority
            )
            file.priority = new_priority

        # Handle RETURNED action
        is_returned = False
        actual_return_date = None
        if action == 'RETURNED':
            is_returned = True
            actual_return_date = timezone.now().date()

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
        )
        movement.save()

        # Update file
        file.current_holder = to_holder
        file.status = 'IN_TRANSIT'

        # Add timeline entry
        notes = remarks or f"File {action.lower()} by {from_holder.get_full_name() or from_holder.username}"
        if to_holder:
            notes = f"File moved to {to_holder.get_full_name() or to_holder.username}: {action}"

        update_fields = ['current_holder', 'status', 'status_timeline']
        if action == 'ESCALATED':
            update_fields.append('priority')

        FileMovementService._add_timeline_entry(
            file, file.status, from_holder, action, notes
        )
        file.save(update_fields=update_fields)

        return movement

    @staticmethod
    def receive_file(*, file, received_by, notes=''):
        """
        Mark file as received by current holder.
        Validates: received_by == file.current_holder
        Records SUBMITTED movement (closest available action for receive)
        Updates status to ACTIVE if was IN_TRANSIT
        Updates status_timeline
        """
        if received_by != file.current_holder:
            raise ValueError(
                f"User {received_by} is not the current holder of file {file.file_number}. "
                f"Current holder is {file.current_holder}."
            )

        # Mark last movement as returned
        last_movement = FileMovement.objects.filter(
            file=file
        ).order_by('-movement_date').first()
        if last_movement and not last_movement.is_returned:
            last_movement.is_returned = True
            last_movement.actual_return_date = timezone.now().date()
            last_movement.completion_notes = notes
            last_movement.save(update_fields=[
                'is_returned', 'actual_return_date', 'completion_notes'
            ])

        # Update file status
        if file.status == 'IN_TRANSIT':
            file.status = 'ACTIVE'
        file.save(update_fields=['status', 'updated_at'])

        # Record receive movement
        movement = FileMovement(
            file=file,
            from_holder=received_by,
            to_holder=None,
            action='SUBMITTED',
            remarks=notes or f"File received by {received_by.get_full_name() or received_by.username}",
            is_returned=True,
            actual_return_date=timezone.now().date(),
            completion_notes=notes,
        )
        movement.save()

        # Add timeline entry
        FileMovementService._add_timeline_entry(
            file, file.status, received_by, 'RECEIVED',
            notes or f"Received by {received_by.get_full_name() or received_by.username}"
        )
        file.save(update_fields=['status_timeline'])

        return movement

    @staticmethod
    def recall_file(*, file, recalled_by, reason=''):
        """
        Recall a file from current holder back to sender.
        Validates: recalled_by must be previous movement's from_holder
        Moves: file.current_holder = recalled_by
        Records RETURNED movement
        Updates status_timeline
        """
        # Find the previous movement where this user was the sender
        previous_movement = FileMovement.objects.filter(
            file=file,
            from_holder=recalled_by
        ).order_by('-movement_date').first()

        if not previous_movement:
            raise ValueError(
                f"User {recalled_by} cannot recall file {file.file_number} "
                f"as they were not the previous sender."
            )

        # Move file back
        file.current_holder = recalled_by
        file.save(update_fields=['current_holder', 'updated_at'])

        # Record RETURNED movement
        movement = FileMovement(
            file=file,
            from_holder=recalled_by,
            to_holder=previous_movement.to_holder,
            action='RETURNED',
            remarks=reason or f"File recalled by {recalled_by.get_full_name() or recalled_by.username}",
            is_returned=True,
            actual_return_date=timezone.now().date(),
        )
        movement.save()

        # Add timeline entry
        FileMovementService._add_timeline_entry(
            file, file.status, recalled_by, 'RETURNED',
            reason or f"File recalled by {recalled_by.get_full_name() or recalled_by.username}"
        )
        file.save(update_fields=['status_timeline'])

        return movement

    @staticmethod
    def escalate_file(*, file, escalated_by, reason=''):
        """
        Escalate file priority and notify.
        Escalates priority: NORMAL->HIGH, HIGH->URGENT
        Records ESCALATED movement
        Updates status_timeline
        """
        # Increment priority
        old_priority = file.priority
        new_priority = FileMovementService.PRIORITY_ESCALATION.get(
            file.priority, file.priority
        )
        file.priority = new_priority

        # Record ESCALATED movement (no specific target holder)
        movement = FileMovement(
            file=file,
            from_holder=escalated_by,
            to_holder=file.current_holder,
            action='ESCALATED',
            remarks=reason or f"File escalated from {old_priority} to {new_priority}",
        )
        movement.save()

        # Add timeline entry
        FileMovementService._add_timeline_entry(
            file, file.status, escalated_by, 'ESCALATED',
            reason or f"Escalated from {old_priority} to {new_priority}"
        )
        file.save(update_fields=['priority', 'status_timeline', 'updated_at'])

        return movement

    @staticmethod
    def archive_file(*, file, archived_by, notes=''):
        """
        Archive a completed file.
        Validates: file.status must be CLOSED or ARCHIVED (COMPLETED is not a valid status)
        Sets: file.status = ARCHIVED
        Records ARCHIVED movement
        Updates status_timeline
        """
        valid_statuses = ['CLOSED', 'ARCHIVED']
        if file.status not in valid_statuses:
            raise ValueError(
                f"Cannot archive file {file.file_number} with status {file.status}. "
                f"File must be in {valid_statuses} status."
            )

        file.status = 'ARCHIVED'
        file.save(update_fields=['status', 'updated_at'])

        # Record ARCHIVED movement
        movement = FileMovement(
            file=file,
            from_holder=archived_by,
            to_holder=None,
            action='ARCHIVED',
            remarks=notes or f"File archived by {archived_by.get_full_name() or archived_by.username}",
        )
        movement.save()

        # Add timeline entry
        FileMovementService._add_timeline_entry(
            file, file.status, archived_by, 'ARCHIVED',
            notes or f"Archived by {archived_by.get_full_name() or archived_by.username}"
        )
        file.save(update_fields=['status_timeline'])

        return movement

    @staticmethod
    def get_file_timeline(file):
        """Return chronological list of all movements for a file."""
        movements = FileMovement.objects.filter(
            file=file
        ).order_by('movement_date')

        timeline = []
        for m in movements:
            timeline.append({
                'timestamp': m.movement_date.isoformat(),
                'action': m.action,
                'from_holder_id': m.from_holder_id,
                'from_holder_name': m.from_holder.get_full_name() or m.from_holder.username if m.from_holder else None,
                'to_holder_id': m.to_holder_id,
                'to_holder_name': m.to_holder.get_full_name() or m.to_holder.username if m.to_holder else None,
                'remarks': m.remarks,
                'status': file.status,
                'is_returned': m.is_returned,
            })

        return timeline

    @staticmethod
    def get_user_pending_files(user):
        """Return all files where user is current_holder and status is ACTIVE/PENDING."""
        return File.objects.filter(
            current_holder=user,
            status__in=['ACTIVE', 'PENDING']
        ).select_related('created_by', 'current_holder', 'department', 'school')

    @staticmethod
    def get_department_files(department, status=None):
        """Return files for a department, optionally filtered by status."""
        qs = File.objects.filter(department=department)
        if status:
            qs = qs.filter(status=status)
        return qs.select_related('created_by', 'current_holder', 'school')

    @staticmethod
    def search_files(query=None, file_type=None, status=None, classification=None,
                     priority=None, department=None, date_from=None, date_to=None,
                     created_by=None, current_holder=None):
        """Full-text search with multiple filters."""
        qs = File.objects.all()

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

        return qs.select_related('created_by', 'current_holder', 'department', 'school')
