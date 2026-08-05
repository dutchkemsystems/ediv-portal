"""Tests for OfflineSyncService."""
from django.test import TestCase
from django.utils import timezone
from apps.users.models import User
from apps.files.models import File, FileMovement, OfflineQueue
from apps.files.services.offline_sync_service import OfflineSyncService


class OfflineSyncServiceQueueTest(TestCase):
    """Tests for queue_action."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='offline@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Offline',
            last_name='User',
            role='TCH'
        )

    def test_queue_action_creates_entry(self):
        """queue_action should create an OfflineQueue entry."""
        item = OfflineSyncService.queue_action(
            user=self.user,
            object_id='file-123',
            action_type='CREATE',
            data={'title': 'Offline File'},
        )
        self.assertIsNotNone(item.id)
        self.assertEqual(item.status, 'PENDING')
        self.assertEqual(item.action_type, 'CREATE')

    def test_queue_multiple_actions(self):
        """Multiple actions should create multiple entries."""
        OfflineSyncService.queue_action(
            user=self.user, object_id='1', action_type='CREATE', data={},
        )
        OfflineSyncService.queue_action(
            user=self.user, object_id='2', action_type='UPDATE', data={},
        )
        self.assertEqual(OfflineQueue.objects.filter(user=self.user).count(), 2)


class OfflineSyncServiceProcessTest(TestCase):
    """Tests for process_queue."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='processor@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Processor',
            last_name='User',
            role='SYSADMIN'
        )

    def test_process_create_action(self):
        """Processing CREATE action should create a File."""
        item = OfflineSyncService.queue_action(
            user=self.user,
            object_id='new-file',
            action_type='CREATE',
            data={
                'file_number': 'EDIV-2026-OFF-001',
                'title': 'Offline Created File',
                'file_type': 'MEMO',
                'file_category': 'ADMIN',
            },
        )
        result = OfflineSyncService.process_queue(user=self.user)
        self.assertEqual(result['processed'], 1)
        self.assertEqual(result['failed'], 0)
        self.assertTrue(File.objects.filter(file_number='EDIV-2026-OFF-001').exists())

    def test_process_update_action(self):
        """Processing UPDATE action should update a File."""
        file_obj = File.objects.create(
            file_number='EDIV-2026-OFF-002',
            title='Original Title',
            file_type='MEMO',
            file_category='ADMIN',
            created_by=self.user,
            current_holder=self.user,
        )
        item = OfflineSyncService.queue_action(
            user=self.user,
            object_id=str(file_obj.id),
            action_type='UPDATE',
            data={'title': 'Updated Title'},
        )
        result = OfflineSyncService.process_queue(user=self.user)
        self.assertEqual(result['processed'], 1)
        file_obj.refresh_from_db()
        self.assertEqual(file_obj.title, 'Updated Title')

    def test_process_completed_items_marked(self):
        """Processed items should be marked COMPLETED."""
        item = OfflineSyncService.queue_action(
            user=self.user,
            object_id='obj-1',
            action_type='CREATE',
            data={'file_number': 'EDIV-2026-OFF-003', 'title': 'Test', 'file_type': 'OTHER', 'file_category': 'ADMIN'},
        )
        OfflineSyncService.process_queue(user=self.user)
        item.refresh_from_db()
        self.assertEqual(item.status, 'COMPLETED')
        self.assertIsNotNone(item.processed_at)

    def test_get_pending_count(self):
        """get_pending_count should return pending items count."""
        OfflineSyncService.queue_action(
            user=self.user, object_id='1', action_type='CREATE', data={},
        )
        OfflineSyncService.queue_action(
            user=self.user, object_id='2', action_type='CREATE', data={},
        )
        count = OfflineSyncService.get_pending_count(user=self.user)
        self.assertEqual(count, 2)

    def test_retry_failed_items(self):
        """retry_failed should reset failed items to pending."""
        item = OfflineQueue.objects.create(
            object_id='bad-item',
            action_type='CREATE',
            user=self.user,
            status='FAILED',
            error_message='Some error',
            attempt_count=1,
        )
        result = OfflineSyncService.retry_failed(user=self.user)
        self.assertEqual(result['retried'], 1)
        item.refresh_from_db()
        self.assertEqual(item.status, 'PENDING')

    def test_process_move_action(self):
        """Processing MOVE action should create a movement."""
        file_obj = File.objects.create(
            file_number='EDIV-2026-OFF-004',
            title='Move Test',
            file_type='MEMO',
            file_category='ADMIN',
            created_by=self.user,
            current_holder=self.user,
        )
        other_user = User.objects.create_user(
            email='target@ediv.gov.ng', password='Test123!@#',
            first_name='Target', last_name='User', role='TCH'
        )
        item = OfflineSyncService.queue_action(
            user=self.user,
            object_id=str(file_obj.id),
            action_type='MOVE',
            data={
                'to_holder_id': other_user.id,
                'action': 'FORWARDED',
                'remarks': 'Offline move',
            },
        )
        result = OfflineSyncService.process_queue(user=self.user)
        self.assertEqual(result['processed'], 1)
        file_obj.refresh_from_db()
        self.assertEqual(file_obj.current_holder, other_user)

    def test_clear_completed(self):
        """clear_completed should remove old completed items."""
        item = OfflineQueue.objects.create(
            object_id='old-item',
            action_type='CREATE',
            user=self.user,
            status='COMPLETED',
            processed_at=timezone.now() - timezone.timedelta(days=60),
        )
        count = OfflineSyncService.clear_completed(older_than_days=30)
        self.assertEqual(count, 1)
        self.assertFalse(OfflineQueue.objects.filter(id=item.id).exists())
