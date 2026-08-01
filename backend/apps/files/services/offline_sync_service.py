"""Offline sync service for mobile support."""
import logging
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)


class OfflineSyncService:
    """Service for processing offline queue items from mobile devices."""

    @staticmethod
    def queue_action(*, user, object_id, action_type, data) -> 'OfflineQueue':
        """Add an action to the offline queue."""
        from apps.files.models import OfflineQueue

        queue_item = OfflineQueue.objects.create(
            object_id=object_id,
            action_type=action_type,
            user=user,
            data=data,
            status='PENDING'
        )
        logger.info(f"Queued offline action: {action_type} for {object_id} by {user.username}")
        return queue_item

    @staticmethod
    def process_queue(*, user=None, limit=100) -> dict:
        """
        Process pending items in the offline queue.

        Returns: {'processed': int, 'failed': int, 'errors': list}
        """
        from apps.files.models import OfflineQueue, File

        qs = OfflineQueue.objects.filter(status='PENDING')
        if user:
            qs = qs.filter(user=user)

        items = qs.order_by('created_at')[:limit]
        processed = 0
        failed = 0
        errors = []

        for item in items:
            item.status = 'PROCESSING'
            item.save()

            try:
                if item.action_type == 'CREATE':
                    # Create file directly using File model
                    file_data = item.data.copy()
                    file_number = file_data.pop('file_number', None)
                    if not file_number:
                        # Auto-generate file number
                        count = File.objects.count() + 1
                        file_number = f"EDIV-OFF-{timezone.now().year}-{count:04d}"
                    File.objects.create(
                        file_number=file_number,
                        created_by=item.user,
                        current_holder=item.user,
                        **{k: v for k, v in file_data.items() if hasattr(File, k)},
                    )

                elif item.action_type == 'MOVE':
                    file = File.objects.get(id=item.object_id)
                    move_data = item.data
                    to_holder_id = move_data.get('to_holder_id')
                    if to_holder_id:
                        to_holder = User.objects.get(id=to_holder_id)
                        from apps.files.models import FileMovement
                        FileMovement.objects.create(
                            file=file,
                            from_holder=item.user,
                            to_holder=to_holder,
                            action=move_data.get('action', 'FORWARDED'),
                            remarks=move_data.get('remarks', ''),
                        )
                        file.current_holder = to_holder
                        file.status = 'IN_TRANSIT'
                        file.save(update_fields=['current_holder', 'status', 'updated_at'])

                elif item.action_type == 'UPDATE':
                    file = File.objects.get(id=item.object_id)
                    update_fields = []
                    for key, value in item.data.items():
                        if hasattr(file, key):
                            setattr(file, key, value)
                            update_fields.append(key)
                    if update_fields:
                        update_fields.append('updated_at')
                        file.save(update_fields=update_fields)

                elif item.action_type == 'ARCHIVE':
                    file = File.objects.get(id=item.object_id)
                    file.status = 'ARCHIVED'
                    file.save(update_fields=['status', 'updated_at'])
                    # Log the archive movement
                    from apps.files.models import FileMovement
                    FileMovement.objects.create(
                        file=file,
                        from_holder=item.user,
                        to_holder=None,
                        action='ARCHIVED',
                        remarks=item.data.get('remarks', 'Archived via offline sync'),
                    )

                item.status = 'COMPLETED'
                item.processed_at = timezone.now()
                item.save()
                processed += 1

            except Exception as e:
                item.status = 'FAILED'
                item.error_message = str(e)
                item.attempt_count += 1
                item.save()
                failed += 1
                errors.append({'item_id': item.id, 'error': str(e)})
                logger.error(f"Failed to process offline item {item.id}: {e}")

        return {'processed': processed, 'failed': failed, 'errors': errors}

    @staticmethod
    def get_pending_count(user=None) -> int:
        """Get count of pending items in queue."""
        from apps.files.models import OfflineQueue

        qs = OfflineQueue.objects.filter(status='PENDING')
        if user:
            qs = qs.filter(user=user)
        return qs.count()

    @staticmethod
    def retry_failed(*, user=None, max_attempts=3) -> dict:
        """Retry failed items that haven't exceeded max attempts."""
        from apps.files.models import OfflineQueue

        qs = OfflineQueue.objects.filter(
            status='FAILED',
            attempt_count__lt=max_attempts
        )
        if user:
            qs = qs.filter(user=user)

        # Reset to pending for retry
        count = qs.update(status='PENDING', error_message='')

        return {'retried': count}

    @staticmethod
    def clear_completed(*, user=None, older_than_days=30) -> int:
        """Clear old completed items from queue."""
        from apps.files.models import OfflineQueue

        cutoff = timezone.now() - timezone.timedelta(days=older_than_days)
        qs = OfflineQueue.objects.filter(
            status='COMPLETED',
            processed_at__lt=cutoff
        )
        if user:
            qs = qs.filter(user=user)

        count = qs.count()
        qs.delete()
        return count
