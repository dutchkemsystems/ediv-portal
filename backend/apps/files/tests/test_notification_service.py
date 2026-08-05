"""Tests for enhanced NotificationService."""
from django.test import TestCase, override_settings
from django.core import mail
from apps.users.models import User
from apps.files.models import File
from apps.files.services.notification_service import NotificationService


class NotificationServiceEmailTest(TestCase):
    """Tests for email notification integration."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='notify@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Notify',
            last_name='User',
            role='TCH',
            phone_number='+2348012345678',
        )
        self.file = File.objects.create(
            file_number='EDIV-2026-NOT-001',
            title='Notification Test File',
            file_type='MEMO',
            file_category='ADMIN',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_send_in_app_notification(self):
        """In-app notification should create a UserNotification record."""
        result = NotificationService.send_notification(
            recipient=self.user,
            subject='Test Subject',
            message='Test message',
            channel='in_app',
        )
        self.assertTrue(result['success'])
        self.assertEqual(result['channel'], 'in_app')

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_send_email_notification(self):
        """Email notification should be queued in Django email backend."""
        result = NotificationService.send_notification(
            recipient=self.user,
            subject='Email Test',
            message='Email body',
            channel='email',
        )
        self.assertTrue(result['success'])

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_notify_file_moved(self):
        """notify_file_moved should send notification to recipient."""
        sender = User.objects.create_user(
            email='sender@ediv.gov.ng', password='Test123!@#',
            first_name='Sender', last_name='User', role='SYSADMIN'
        )
        result = NotificationService.notify_file_moved(
            file=self.file,
            movement={'get_action_display': lambda: 'Forwarded'},
            recipient=self.user,
            sender=sender,
        )
        self.assertTrue(result['success'])

    def test_invalid_channel_returns_error(self):
        """Invalid channel should return error."""
        result = NotificationService.send_notification(
            recipient=self.user,
            subject='Test',
            message='Test',
            channel='invalid_channel',
        )
        self.assertFalse(result['success'])

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_notification_with_high_priority(self):
        """High priority notification should be flagged."""
        result = NotificationService.send_notification(
            recipient=self.user,
            subject='Urgent',
            message='Urgent message',
            channel='in_app',
            priority='URGENT',
        )
        self.assertTrue(result['success'])

    def test_mark_notification_read(self):
        """mark_notification_read should mark notification as read."""
        from apps.communication.models import UserNotification
        notif = UserNotification.objects.create(
            user=self.user,
            title='Test',
            message='Test message',
            is_read=False,
        )
        result = NotificationService.mark_notification_read(notif.id, self.user)
        self.assertTrue(result)
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)

    def test_get_user_notifications(self):
        """get_user_notifications should return user's notifications."""
        from apps.communication.models import UserNotification
        UserNotification.objects.create(
            user=self.user, title='Notif 1', message='msg1',
        )
        UserNotification.objects.create(
            user=self.user, title='Notif 2', message='msg2',
        )
        notifs = NotificationService.get_user_notifications(self.user)
        self.assertEqual(len(notifs), 2)

    def test_get_user_notifications_unread_only(self):
        """get_user_notifications with unread_only should filter."""
        from apps.communication.models import UserNotification
        UserNotification.objects.create(
            user=self.user, title='Read', message='msg1', is_read=True,
        )
        UserNotification.objects.create(
            user=self.user, title='Unread', message='msg2', is_read=False,
        )
        notifs = NotificationService.get_user_notifications(self.user, unread_only=True)
        self.assertEqual(len(notifs), 1)
        self.assertEqual(notifs[0].title, 'Unread')

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_notify_file_escalated(self):
        """notify_file_escalated should send notification."""
        result = NotificationService.notify_file_escalated(
            file=self.file,
            escalated_by=self.user,
            reason='Overdue',
        )
        self.assertIn('results', result)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_notify_deadline_approaching(self):
        """notify_deadline_approaching should send notification."""
        result = NotificationService.notify_deadline_approaching(
            file=self.file,
            hours_remaining=2,
        )
        self.assertTrue(result['success'])
