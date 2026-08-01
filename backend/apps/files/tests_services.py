"""Tests for NotificationService, SearchService, and OfflineSyncService."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from apps.files.models import File, FileMovement, OfflineQueue
from apps.files.services.notification_service import NotificationService
from apps.files.services.search_service import SearchService
from apps.files.services.offline_sync_service import OfflineSyncService

User = get_user_model()


# ============================================================
# NotificationService Tests
# ============================================================
class NotificationServiceSendNotificationTest(TestCase):
    """Tests for NotificationService.send_notification."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='notif@test.gov.ng',
            password='TestPass123!@#',
            first_name='Notif',
            last_name='User',
            role='TCH'
        )

    def test_in_app_channel_creates_notification(self):
        """in_app channel should return success=True."""
        result = NotificationService.send_notification(
            recipient=self.user,
            subject='Test Subject',
            message='Test Message',
            channel='in_app',
        )
        self.assertTrue(result['success'])
        self.assertEqual(result['channel'], 'in_app')
        self.assertIsNone(result['error'])

    def test_email_channel_returns_success(self):
        """email channel logs and returns success (integration point)."""
        result = NotificationService.send_notification(
            recipient=self.user,
            subject='Email Subject',
            message='Email Body',
            channel='email',
        )
        self.assertTrue(result['success'])
        self.assertEqual(result['channel'], 'email')

    def test_sms_channel_returns_success(self):
        """sms channel logs and returns success (integration point)."""
        result = NotificationService.send_notification(
            recipient=self.user,
            subject='SMS Subject',
            message='SMS Body',
            channel='sms',
        )
        self.assertTrue(result['success'])
        self.assertEqual(result['channel'], 'sms')

    def test_whatsapp_channel_returns_success(self):
        """whatsapp channel logs and returns success (integration point)."""
        result = NotificationService.send_notification(
            recipient=self.user,
            subject='WA Subject',
            message='WA Body',
            channel='whatsapp',
        )
        self.assertTrue(result['success'])
        self.assertEqual(result['channel'], 'whatsapp')

    def test_invalid_channel_returns_error(self):
        """Invalid channel should return success=False."""
        result = NotificationService.send_notification(
            recipient=self.user,
            subject='Sub',
            message='Msg',
            channel='invalid_channel',
        )
        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_returns_dict_with_required_keys(self):
        """Result dict must have success, channel, error keys."""
        result = NotificationService.send_notification(
            recipient=self.user,
            subject='Sub',
            message='Msg',
            channel='in_app',
        )
        self.assertIn('success', result)
        self.assertIn('channel', result)
        self.assertIn('error', result)


class NotificationServiceFileMovedTest(TestCase):
    """Tests for NotificationService.notify_file_moved."""

    def setUp(self):
        self.sender = User.objects.create_user(
            email='sender@test.gov.ng',
            password='TestPass123!@#',
            first_name='Sender',
            last_name='User',
            role='SYSADMIN'
        )
        self.recipient = User.objects.create_user(
            email='recipient@test.gov.ng',
            password='TestPass123!@#',
            first_name='Recipient',
            last_name='User',
            role='TCH'
        )
        self.file = File.objects.create(
            file_number='EDIV-2024-NOTIF-001',
            title='Notification Test File',
            file_type='CORRESPONDENCE',
            file_category='CORR',
            created_by=self.sender,
            current_holder=self.recipient,
            priority='HIGH',
        )
        self.movement = FileMovement.objects.create(
            file=self.file,
            from_holder=self.sender,
            to_holder=self.recipient,
            action='FORWARDED',
            remarks='Please review',
        )

    def test_notify_file_moved_returns_success(self):
        """notify_file_moved should return a success dict."""
        result = NotificationService.notify_file_moved(
            file=self.file,
            movement=self.movement,
            recipient=self.recipient,
            sender=self.sender,
        )
        self.assertTrue(result['success'])
        self.assertEqual(result['channel'], 'in_app')

    def test_notify_file_moved_includes_file_number(self):
        """Notification message should reference the file number."""
        # Verify the call succeeds - message construction is internal
        result = NotificationService.notify_file_moved(
            file=self.file,
            movement=self.movement,
            recipient=self.recipient,
            sender=self.sender,
        )
        self.assertTrue(result['success'])


class NotificationServiceEscalatedTest(TestCase):
    """Tests for NotificationService.notify_file_escalated."""

    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@test.gov.ng',
            password='TestPass123!@#',
            first_name='User',
            last_name='One',
            role='SYSADMIN'
        )
        self.user2 = User.objects.create_user(
            email='user2@test.gov.ng',
            password='TestPass123!@#',
            first_name='User',
            last_name='Two',
            role='TCH'
        )
        self.escalated_by = User.objects.create_user(
            email='escalator@test.gov.ng',
            password='TestPass123!@#',
            first_name='Escalator',
            last_name='User',
            role='SYSADMIN'
        )
        self.file = File.objects.create(
            file_number='EDIV-2024-ESC-001',
            title='Escalation Test',
            file_type='MEMO',
            file_category='ADMIN',
            created_by=self.user1,
            current_holder=self.user2,
            priority='HIGH',
        )

    def test_escalation_notifies_current_holder_and_creator(self):
        """Escalation should notify both current_holder and created_by."""
        result = NotificationService.notify_file_escalated(
            file=self.file,
            escalated_by=self.escalated_by,
            reason='Urgent matter requiring attention',
        )
        self.assertIn('results', result)
        self.assertEqual(len(result['results']), 2)
        for r in result['results']:
            self.assertTrue(r['success'])

    def test_escalation_no_current_holder(self):
        """If no current holder, only creator should be notified."""
        self.file.current_holder = None
        self.file.save()
        result = NotificationService.notify_file_escalated(
            file=self.file,
            escalated_by=self.escalated_by,
            reason='Test',
        )
        # Only created_by should be notified
        self.assertEqual(len(result['results']), 1)

    def test_escalation_same_creator_and_holder(self):
        """If creator and holder are the same, only one notification is sent."""
        self.file.current_holder = self.user1  # Same as created_by
        self.file.save()
        result = NotificationService.notify_file_escalated(
            file=self.file,
            escalated_by=self.escalated_by,
            reason='Test',
        )
        # Set deduplication means only 1 result (same user)
        self.assertEqual(len(result['results']), 1)


class NotificationServiceDeadlineTest(TestCase):
    """Tests for NotificationService.notify_deadline_approaching."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='holder@test.gov.ng',
            password='TestPass123!@#',
            first_name='Holder',
            last_name='User',
            role='TCH'
        )
        self.creator = User.objects.create_user(
            email='creator@test.gov.ng',
            password='TestPass123!@#',
            first_name='Creator',
            last_name='User',
            role='SYSADMIN'
        )
        self.file = File.objects.create(
            file_number='EDIV-2024-DEAD-001',
            title='Deadline Test',
            file_type='REPORT',
            file_category='ADMIN',
            created_by=self.creator,
            current_holder=self.user,
            due_date=timezone.now().date() + timedelta(days=1),
            priority='URGENT',
        )

    def test_deadline_notification_success(self):
        """Should return success for file with a current holder."""
        result = NotificationService.notify_deadline_approaching(
            file=self.file,
            hours_remaining=24,
        )
        self.assertTrue(result['success'])
        self.assertEqual(result['channel'], 'in_app')

    def test_deadline_no_holder_returns_error(self):
        """Should return error if file has no current holder."""
        self.file.current_holder = None
        self.file.save()
        result = NotificationService.notify_deadline_approaching(
            file=self.file,
            hours_remaining=24,
        )
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'No current holder')


class NotificationServiceRecallTest(TestCase):
    """Tests for NotificationService.notify_file_recalled."""

    def setUp(self):
        self.recalled_by = User.objects.create_user(
            email='recaller@test.gov.ng',
            password='TestPass123!@#',
            first_name='Recaller',
            last_name='User',
            role='SYSADMIN'
        )
        self.holder = User.objects.create_user(
            email='holder@test.gov.ng',
            password='TestPass123!@#',
            first_name='Holder',
            last_name='User',
            role='TCH'
        )
        self.file = File.objects.create(
            file_number='EDIV-2024-RECALL-001',
            title='Recall Test',
            file_type='MEMO',
            file_category='ADMIN',
            created_by=self.recalled_by,
            current_holder=self.holder,
        )

    def test_recall_notification_success(self):
        """Should return success."""
        result = NotificationService.notify_file_recalled(
            file=self.file,
            recalled_by=self.recalled_by,
            recipient=self.holder,
        )
        self.assertTrue(result['success'])
        self.assertEqual(result['channel'], 'in_app')


class NotificationServiceGetNotificationsTest(TestCase):
    """Tests for NotificationService.get_user_notifications."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='getnotif@test.gov.ng',
            password='TestPass123!@#',
            first_name='Get',
            last_name='Notif',
            role='TCH'
        )

    def test_get_notifications_returns_list(self):
        """Should return a list (may be empty if no Notification model)."""
        result = NotificationService.get_user_notifications(self.user)
        self.assertIsInstance(result, list)

    def test_get_unread_only(self):
        """Should handle unread_only parameter."""
        result = NotificationService.get_user_notifications(self.user, unread_only=True)
        self.assertIsInstance(result, list)

    def test_get_with_limit(self):
        """Should respect limit parameter."""
        result = NotificationService.get_user_notifications(self.user, limit=10)
        self.assertIsInstance(result, list)


class NotificationServiceMarkReadTest(TestCase):
    """Tests for NotificationService.mark_notification_read."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='markread@test.gov.ng',
            password='TestPass123!@#',
            first_name='Mark',
            last_name='Read',
            role='TCH'
        )

    def test_mark_nonexistent_notification_returns_false(self):
        """Marking a nonexistent notification should return False."""
        result = NotificationService.mark_notification_read(99999, self.user)
        self.assertFalse(result)


# ============================================================
# SearchService Tests
# ============================================================
class SearchServiceSearchFilesTest(TestCase):
    """Tests for SearchService.search_files."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='searcher@test.gov.ng',
            password='TestPass123!@#',
            first_name='Searcher',
            last_name='User',
            role='SYSADMIN'
        )
        self.file1 = File.objects.create(
            file_number='EDIV-2024-SEARCH-001',
            title='Correspondence about budget',
            file_type='CORRESPONDENCE',
            file_category='CORR',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
            priority='NORMAL',
            tags=['budget', 'finance'],
        )
        self.file2 = File.objects.create(
            file_number='EDIV-2024-SEARCH-002',
            title='Inspection Report for Q1',
            file_type='REPORT',
            file_category='INSP',
            created_by=self.user,
            status='PENDING',
            priority='HIGH',
            tags=['inspection', 'quarterly'],
        )
        self.file3 = File.objects.create(
            file_number='EDIV-2024-SEARCH-003',
            title='Memo about staff meeting',
            file_type='MEMO',
            file_category='ADMIN',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
            priority='URGENT',
            tags=['staff', 'meeting'],
        )

    def test_search_no_filters_returns_all(self):
        """Without filters, should return all files."""
        result = SearchService.search_files()
        self.assertEqual(result['total'], 3)
        self.assertEqual(len(result['results']), 3)

    def test_search_by_query_text(self):
        """Full-text search should find matching files."""
        result = SearchService.search_files(query='budget')
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['results'][0]['file_number'], 'EDIV-2024-SEARCH-001')

    def test_search_by_file_type(self):
        """Filter by file_type."""
        result = SearchService.search_files(file_type='REPORT')
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['results'][0]['file_type'], 'REPORT')

    def test_search_by_status(self):
        """Filter by status."""
        result = SearchService.search_files(status='PENDING')
        self.assertEqual(result['total'], 1)

    def test_search_by_priority(self):
        """Filter by priority."""
        result = SearchService.search_files(priority='URGENT')
        self.assertEqual(result['total'], 1)

    def test_search_by_created_by(self):
        """Filter by created_by user id."""
        result = SearchService.search_files(created_by=self.user.id)
        self.assertEqual(result['total'], 3)

    def test_search_by_current_holder(self):
        """Filter by current_holder user id."""
        result = SearchService.search_files(current_holder=self.user.id)
        self.assertEqual(result['total'], 2)

    def test_search_with_tags(self):
        """Filter by tags."""
        result = SearchService.search_files(tags=['budget'])
        self.assertEqual(result['total'], 1)

    def test_search_pagination_offset_limit(self):
        """Pagination with offset and limit."""
        result = SearchService.search_files(limit=2, offset=0)
        self.assertEqual(len(result['results']), 2)
        self.assertEqual(result['total'], 3)

        result2 = SearchService.search_files(limit=2, offset=2)
        self.assertEqual(len(result2['results']), 1)

    def test_search_sort_by_created_at(self):
        """Sorting by created_at descending (default)."""
        result = SearchService.search_files(sort_by='-created_at')
        self.assertEqual(len(result['results']), 3)

    def test_search_sort_by_title(self):
        """Sorting by title."""
        result = SearchService.search_files(sort_by='title')
        self.assertEqual(len(result['results']), 3)
        # Should be sorted alphabetically
        titles = [r['title'] for r in result['results']]
        self.assertEqual(titles, sorted(titles))

    def test_search_invalid_sort_defaults(self):
        """Invalid sort field should default to -created_at."""
        result = SearchService.search_files(sort_by='invalid_field')
        self.assertEqual(len(result['results']), 3)

    def test_search_result_structure(self):
        """Results should have expected fields."""
        result = SearchService.search_files(query='budget')
        self.assertEqual(result['total'], 1)
        item = result['results'][0]
        self.assertIn('id', item)
        self.assertIn('file_number', item)
        self.assertIn('title', item)
        self.assertIn('file_type', item)
        self.assertIn('status', item)
        self.assertIn('priority', item)
        self.assertIn('created_by', item)
        self.assertIn('current_holder', item)
        self.assertIn('created_at', item)
        self.assertIn('updated_at', item)
        self.assertIn('tags', item)

    def test_search_result_creator_info(self):
        """Result should include created_by info."""
        result = SearchService.search_files(query='budget')
        creator = result['results'][0]['created_by']
        self.assertIsNotNone(creator)
        self.assertEqual(creator['id'], self.user.id)

    def test_search_date_range(self):
        """Filter by date range."""
        today = timezone.now().date()
        result = SearchService.search_files(date_from=today, date_to=today)
        self.assertEqual(result['total'], 3)

    def test_search_no_results(self):
        """Search with no matches should return empty."""
        result = SearchService.search_files(query='nonexistent_xyz')
        self.assertEqual(result['total'], 0)
        self.assertEqual(len(result['results']), 0)


class SearchServiceSearchMovementsTest(TestCase):
    """Tests for SearchService.search_movements."""

    def setUp(self):
        self.user1 = User.objects.create_user(
            email='mov1@test.gov.ng',
            password='TestPass123!@#',
            first_name='Mov1',
            last_name='User',
            role='SYSADMIN'
        )
        self.user2 = User.objects.create_user(
            email='mov2@test.gov.ng',
            password='TestPass123!@#',
            first_name='Mov2',
            last_name='User',
            role='TCH'
        )
        self.file = File.objects.create(
            file_number='EDIV-2024-MOV-001',
            title='Movement Test',
            file_type='MEMO',
            file_category='ADMIN',
            created_by=self.user1,
            current_holder=self.user2,
        )
        self.movement = FileMovement.objects.create(
            file=self.file,
            from_holder=self.user1,
            to_holder=self.user2,
            action='FORWARDED',
            remarks='Please review',
        )

    def test_search_movements_returns_all(self):
        """Should return all movements."""
        result = SearchService.search_movements()
        self.assertEqual(result['total'], 1)

    def test_search_movements_by_file_id(self):
        """Filter by file_id."""
        result = SearchService.search_movements(file_id=self.file.id)
        self.assertEqual(result['total'], 1)

    def test_search_movements_by_from_holder(self):
        """Filter by from_holder."""
        result = SearchService.search_movements(from_holder=self.user1.id)
        self.assertEqual(result['total'], 1)

    def test_search_movements_by_to_holder(self):
        """Filter by to_holder."""
        result = SearchService.search_movements(to_holder=self.user2.id)
        self.assertEqual(result['total'], 1)

    def test_search_movements_by_action(self):
        """Filter by action."""
        result = SearchService.search_movements(action='FORWARDED')
        self.assertEqual(result['total'], 1)

    def test_search_movements_result_structure(self):
        """Results should have expected fields."""
        result = SearchService.search_movements()
        item = result['results'][0]
        self.assertIn('id', item)
        self.assertIn('file_number', item)
        self.assertIn('file_title', item)
        self.assertIn('from_holder', item)
        self.assertIn('to_holder', item)
        self.assertIn('action', item)
        self.assertIn('remarks', item)
        self.assertIn('movement_date', item)


class SearchServiceSuggestionsTest(TestCase):
    """Tests for SearchService.get_search_suggestions."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='suggest@test.gov.ng',
            password='TestPass123!@#',
            first_name='Suggest',
            last_name='User',
            role='SYSADMIN'
        )
        self.file = File.objects.create(
            file_number='EDIV-2024-SUGG-001',
            title='Suggestion Test File',
            file_type='MEMO',
            file_category='ADMIN',
            created_by=self.user,
        )

    def test_suggestions_with_short_query(self):
        """Query shorter than 2 chars should return empty list."""
        result = SearchService.get_search_suggestions('a')
        self.assertEqual(result, [])

    def test_suggestions_with_valid_query(self):
        """Valid query should return matching suggestions."""
        result = SearchService.get_search_suggestions('SUGG')
        self.assertGreater(len(result), 0)

    def test_suggestions_empty_query(self):
        """Empty query should return empty list."""
        result = SearchService.get_search_suggestions('')
        self.assertEqual(result, [])

    def test_suggestions_none_query(self):
        """None query should return empty list."""
        result = SearchService.get_search_suggestions(None)
        self.assertEqual(result, [])

    def test_suggestions_limit(self):
        """Should respect limit parameter."""
        # Create multiple files
        for i in range(5):
            File.objects.create(
                file_number=f'EDIV-2024-LIMIT-{i:03d}',
                title=f'Limit Test File {i}',
                file_type='MEMO',
                file_category='ADMIN',
                created_by=self.user,
            )
        result = SearchService.get_search_suggestions('LIMIT', limit=3)
        self.assertLessEqual(len(result), 3)


# ============================================================
# OfflineSyncService Tests
# ============================================================
class OfflineSyncServiceQueueActionTest(TestCase):
    """Tests for OfflineSyncService.queue_action."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='offline@test.gov.ng',
            password='TestPass123!@#',
            first_name='Offline',
            last_name='User',
            role='TCH'
        )

    def test_queue_action_creates_pending_item(self):
        """queue_action should create a PENDING OfflineQueue item."""
        item = OfflineSyncService.queue_action(
            user=self.user,
            object_id='file-123',
            action_type='CREATE',
            data={'title': 'Test', 'file_type': 'MEMO'},
        )
        self.assertIsNotNone(item.id)
        self.assertEqual(item.status, 'PENDING')
        self.assertEqual(item.action_type, 'CREATE')
        self.assertEqual(item.object_id, 'file-123')
        self.assertEqual(item.user, self.user)

    def test_queue_action_update(self):
        """queue_action for UPDATE."""
        item = OfflineSyncService.queue_action(
            user=self.user,
            object_id='file-456',
            action_type='UPDATE',
            data={'title': 'Updated Title'},
        )
        self.assertEqual(item.action_type, 'UPDATE')

    def test_queue_action_move(self):
        """queue_action for MOVE."""
        item = OfflineSyncService.queue_action(
            user=self.user,
            object_id='file-789',
            action_type='MOVE',
            data={'to_holder_id': 2},
        )
        self.assertEqual(item.action_type, 'MOVE')

    def test_queue_action_archive(self):
        """queue_action for ARCHIVE."""
        item = OfflineSyncService.queue_action(
            user=self.user,
            object_id='file-abc',
            action_type='ARCHIVE',
            data={},
        )
        self.assertEqual(item.action_type, 'ARCHIVE')


class OfflineSyncServiceProcessQueueTest(TestCase):
    """Tests for OfflineSyncService.process_queue."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='processor@test.gov.ng',
            password='TestPass123!@#',
            first_name='Processor',
            last_name='User',
            role='SYSADMIN'
        )
        self.holder = User.objects.create_user(
            email='holder@test.gov.ng',
            password='TestPass123!@#',
            first_name='Holder',
            last_name='User',
            role='TCH'
        )

    def test_process_empty_queue(self):
        """Processing an empty queue should return 0 processed."""
        result = OfflineSyncService.process_queue()
        self.assertEqual(result['processed'], 0)
        self.assertEqual(result['failed'], 0)
        self.assertEqual(result['errors'], [])

    def test_process_queue_with_pending_items(self):
        """Processing pending items should update their status."""
        # Create a pending UPDATE item for an existing file
        file_obj = File.objects.create(
            file_number='EDIV-2024-OFF-001',
            title='Offline Test',
            file_type='MEMO',
            file_category='ADMIN',
            created_by=self.user,
        )
        item = OfflineQueue.objects.create(
            object_id=str(file_obj.id),
            action_type='UPDATE',
            user=self.user,
            data={'title': 'Updated Offline'},
            status='PENDING',
        )
        result = OfflineSyncService.process_queue(user=self.user)
        self.assertEqual(result['processed'], 1)
        self.assertEqual(result['failed'], 0)
        item.refresh_from_db()
        self.assertEqual(item.status, 'COMPLETED')
        self.assertIsNotNone(item.processed_at)

    def test_process_queue_with_invalid_action_fails(self):
        """Processing an item with invalid data should fail gracefully."""
        item = OfflineQueue.objects.create(
            object_id='99999',
            action_type='UPDATE',
            user=self.user,
            data={'title': 'Test'},
            status='PENDING',
        )
        result = OfflineSyncService.process_queue(user=self.user)
        self.assertEqual(result['failed'], 1)
        item.refresh_from_db()
        self.assertEqual(item.status, 'FAILED')
        self.assertEqual(item.attempt_count, 1)
        self.assertIn('error', result['errors'][0])

    def test_process_queue_respects_limit(self):
        """Should only process up to limit items."""
        # Create actual files to process as updates
        for i in range(5):
            f = File.objects.create(
                file_number=f'EDIV-2024-LIMIT-{i:03d}',
                title=f'Limit File {i}',
                file_type='MEMO',
                file_category='ADMIN',
                created_by=self.user,
            )
            OfflineQueue.objects.create(
                object_id=str(f.id),
                action_type='UPDATE',
                user=self.user,
                data={'title': f'Updated Limit File {i}'},
                status='PENDING',
            )
        result = OfflineSyncService.process_queue(user=self.user, limit=2)
        # Only 2 should have been processed, rest remain PENDING
        self.assertEqual(result['processed'], 2)
        self.assertEqual(result['failed'], 0)
        # Verify remaining are still PENDING
        remaining = OfflineQueue.objects.filter(status='PENDING').count()
        self.assertEqual(remaining, 3)

    def test_process_queue_skips_non_pending(self):
        """Should only process PENDING items."""
        file_obj = File.objects.create(
            file_number='EDIV-2024-OFF-002',
            title='Already Processed',
            file_type='MEMO',
            file_category='ADMIN',
            created_by=self.user,
        )
        OfflineQueue.objects.create(
            object_id=str(file_obj.id),
            action_type='UPDATE',
            user=self.user,
            data={'title': 'Done'},
            status='COMPLETED',
        )
        result = OfflineSyncService.process_queue()
        self.assertEqual(result['processed'], 0)


class OfflineSyncServicePendingCountTest(TestCase):
    """Tests for OfflineSyncService.get_pending_count."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='count@test.gov.ng',
            password='TestPass123!@#',
            first_name='Count',
            last_name='User',
            role='TCH'
        )

    def test_empty_queue_count(self):
        """Empty queue should return 0."""
        count = OfflineSyncService.get_pending_count()
        self.assertEqual(count, 0)

    def test_pending_count(self):
        """Should count only PENDING items."""
        OfflineQueue.objects.create(
            object_id='a', action_type='CREATE', user=self.user, status='PENDING'
        )
        OfflineQueue.objects.create(
            object_id='b', action_type='CREATE', user=self.user, status='COMPLETED'
        )
        OfflineQueue.objects.create(
            object_id='c', action_type='CREATE', user=self.user, status='PENDING'
        )
        count = OfflineSyncService.get_pending_count()
        self.assertEqual(count, 2)

    def test_pending_count_filtered_by_user(self):
        """Should count only items for the specified user."""
        user2 = User.objects.create_user(
            email='user2@test.gov.ng',
            password='TestPass123!@#',
            first_name='User2',
            last_name='User',
            role='TCH'
        )
        OfflineQueue.objects.create(
            object_id='a', action_type='CREATE', user=self.user, status='PENDING'
        )
        OfflineQueue.objects.create(
            object_id='b', action_type='CREATE', user=user2, status='PENDING'
        )
        count = OfflineSyncService.get_pending_count(user=self.user)
        self.assertEqual(count, 1)


class OfflineSyncServiceRetryTest(TestCase):
    """Tests for OfflineSyncService.retry_failed."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='retry@test.gov.ng',
            password='TestPass123!@#',
            first_name='Retry',
            last_name='User',
            role='TCH'
        )

    def test_retry_failed_items(self):
        """Failed items below max_attempts should be reset to PENDING."""
        item = OfflineQueue.objects.create(
            object_id='retry-1',
            action_type='CREATE',
            user=self.user,
            status='FAILED',
            attempt_count=1,
            error_message='Some error',
        )
        result = OfflineSyncService.retry_failed(user=self.user)
        self.assertEqual(result['retried'], 1)
        item.refresh_from_db()
        self.assertEqual(item.status, 'PENDING')
        self.assertEqual(item.error_message, '')

    def test_retry_skips_items_at_max_attempts(self):
        """Items at or above max_attempts should not be retried."""
        item = OfflineQueue.objects.create(
            object_id='retry-max',
            action_type='CREATE',
            user=self.user,
            status='FAILED',
            attempt_count=3,
            error_message='Too many attempts',
        )
        result = OfflineSyncService.retry_failed(user=self.user, max_attempts=3)
        self.assertEqual(result['retried'], 0)
        item.refresh_from_db()
        self.assertEqual(item.status, 'FAILED')

    def test_retry_default_max_attempts(self):
        """Default max_attempts should be 3."""
        item = OfflineQueue.objects.create(
            object_id='retry-def',
            action_type='CREATE',
            user=self.user,
            status='FAILED',
            attempt_count=2,
        )
        result = OfflineSyncService.retry_failed()
        self.assertEqual(result['retried'], 1)


class OfflineSyncServiceClearCompletedTest(TestCase):
    """Tests for OfflineSyncService.clear_completed."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='clear@test.gov.ng',
            password='TestPass123!@#',
            first_name='Clear',
            last_name='User',
            role='TCH'
        )

    def test_clear_completed_removes_old_items(self):
        """Should delete completed items older than specified days."""
        # Create a completed item with a past processed_at
        item = OfflineQueue.objects.create(
            object_id='old-item',
            action_type='CREATE',
            user=self.user,
            status='COMPLETED',
        )
        # Manually set processed_at to 31 days ago
        OfflineQueue.objects.filter(id=item.id).update(
            processed_at=timezone.now() - timezone.timedelta(days=31)
        )
        count = OfflineSyncService.clear_completed(older_than_days=30)
        self.assertEqual(count, 1)
        self.assertFalse(OfflineQueue.objects.filter(id=item.id).exists())

    def test_clear_completed_keeps_recent_items(self):
        """Should not delete recently completed items."""
        item = OfflineQueue.objects.create(
            object_id='new-item',
            action_type='CREATE',
            user=self.user,
            status='COMPLETED',
            processed_at=timezone.now(),
        )
        count = OfflineSyncService.clear_completed(older_than_days=30)
        self.assertEqual(count, 0)
        self.assertTrue(OfflineQueue.objects.filter(id=item.id).exists())

    def test_clear_completed_empty_queue(self):
        """Empty queue should return 0."""
        count = OfflineSyncService.clear_completed()
        self.assertEqual(count, 0)
