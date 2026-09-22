"""Celery tasks for file automation and maintenance."""

import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def check_and_escalate_overdue_files():
    """Periodic task to check for overdue files and auto-escalate."""
    try:
        from apps.files.services.file_movement_service import FileMovementService

        result = FileMovementService.check_and_escalate_overdue()
        logger.info(f"Overdue file check completed: {result}")
        return result
    except Exception as exc:
        logger.error(f"Overdue file check failed: {exc}")
        return {"error": str(exc)}


@shared_task
def process_offline_queue():
    """Periodic task to process offline sync queue."""
    try:
        from apps.files.services.offline_sync_service import OfflineSyncService

        result = OfflineSyncService.process_queue()
        logger.info(f"Offline queue processing completed: {result}")
        return result
    except Exception as exc:
        logger.error(f"Offline queue processing failed: {exc}")
        return {"error": str(exc)}


@shared_task
def send_deadline_reminders():
    """Periodic task to send deadline approaching reminders."""
    try:
        from datetime import timedelta

        from apps.files.models import File
        from apps.files.services.notification_service import NotificationService

        # Find files with deadlines approaching within 4 hours
        deadline_threshold = timezone.now() + timedelta(hours=4)
        files_needing_reminders = File.objects.filter(
            expected_completion_date__lte=deadline_threshold.date(),
            expected_completion_date__gte=timezone.now().date(),
            status__in=["ACTIVE", "IN_TRANSIT", "PENDING"],
        ).select_related("current_holder")

        sent_count = 0
        for file_obj in files_needing_reminders:
            if file_obj.current_holder:
                NotificationService.notify_deadline_approaching(
                    file=file_obj,
                    hours_remaining=4,
                )
                sent_count += 1

        logger.info(f"Deadline reminders sent: {sent_count}")
        return {"reminders_sent": sent_count}
    except Exception as exc:
        logger.error(f"Deadline reminders failed: {exc}")
        return {"error": str(exc)}


@shared_task
def reindex_elasticsearch():
    """Periodic task to reindex all files in Elasticsearch."""
    try:
        from apps.files.services.search_service import SearchService

        result = SearchService.reindex_all()
        logger.info(f"Elasticsearch reindex completed: {result}")
        return result
    except Exception as exc:
        logger.error(f"Elasticsearch reindex failed: {exc}")
        return {"error": str(exc)}
