"""Multi-channel notification service for file movements."""
import logging
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending notifications via multiple channels."""

    CHANNEL_CHOICES = ['email', 'sms', 'whatsapp', 'in_app']

    @staticmethod
    def send_notification(*, recipient, subject, message, channel='in_app',
                         file=None, notification_type='FILE_MOVEMENT',
                         priority='NORMAL', metadata=None) -> dict:
        """
        Send a notification through specified channel.

        Returns: {'success': bool, 'channel': str, 'error': str or None}

        Channels:
        - in_app: Create Notification record (always works)
        - email: Log for now (email service integration point)
        - sms: Log for now (SMS service integration point)
        - whatsapp: Log for now (WhatsApp service integration point)
        """
        if channel not in NotificationService.CHANNEL_CHOICES:
            return {
                'success': False,
                'channel': channel,
                'error': f'Invalid channel: {channel}. Must be one of {NotificationService.CHANNEL_CHOICES}',
            }

        try:
            if channel == 'in_app':
                # Create in-app notification via UserNotification
                from apps.communication.models import UserNotification
                notif_type = 'INFO'
                if priority in ('HIGH', 'URGENT'):
                    notif_type = 'WARNING'
                UserNotification.objects.create(
                    user=recipient,
                    title=subject,
                    message=message,
                    notification_type=notif_type,
                    is_read=False,
                )
                logger.info(f"In-app notification sent to {recipient}: {subject}")

            elif channel == 'email':
                # Integration point for email service (e.g., SendGrid, SES)
                logger.info(f"[EMAIL] To: {recipient.email} | Subject: {subject} | Body: {message}")

            elif channel == 'sms':
                # Integration point for SMS service (e.g., Twilio)
                logger.info(f"[SMS] To: {recipient.phone_number} | Message: {subject}: {message[:100]}")

            elif channel == 'whatsapp':
                # Integration point for WhatsApp API
                logger.info(f"[WHATSAPP] To: {recipient.phone_number} | Message: {subject}: {message[:100]}")

            return {
                'success': True,
                'channel': channel,
                'error': None,
            }

        except Exception as e:
            logger.error(f"Failed to send {channel} notification to {recipient}: {e}")
            return {
                'success': False,
                'channel': channel,
                'error': str(e),
            }

    @staticmethod
    def notify_file_moved(*, file, movement, recipient, sender) -> dict:
        """Send notification when file is moved to a new holder."""
        subject = f"File {file.file_number} assigned to you"
        message = (
            f"File '{file.title}' ({file.file_number}) has been forwarded to you by "
            f"{sender.get_full_name() or sender.username}.\n"
            f"Action: {movement.get_action_display()}\n"
            f"Priority: {file.get_priority_display()}\n"
            f"Remarks: {movement.remarks or 'None'}"
        )
        return NotificationService.send_notification(
            recipient=recipient, subject=subject, message=message,
            file=file, notification_type='FILE_MOVEMENT',
            priority=file.priority
        )

    @staticmethod
    def notify_file_escalated(*, file, escalated_by, reason) -> dict:
        """Send notification when file is escalated."""
        # Notify current_holder and created_by
        recipients = set()
        if file.current_holder:
            recipients.add(file.current_holder)
        if file.created_by:
            recipients.add(file.created_by)

        subject = f"URGENT: File {file.file_number} escalated"
        message = (
            f"File '{file.title}' ({file.file_number}) has been escalated by "
            f"{escalated_by.get_full_name() or escalated_by.username}.\n"
            f"Reason: {reason}\n"
            f"New Priority: {file.get_priority_display()}"
        )

        results = []
        for recipient in recipients:
            results.append(NotificationService.send_notification(
                recipient=recipient, subject=subject, message=message,
                file=file, notification_type='FILE_ESCALATION',
                priority='URGENT'
            ))
        return {'results': results}

    @staticmethod
    def notify_deadline_approaching(*, file, hours_remaining) -> dict:
        """Send notification when file deadline is approaching."""
        if not file.current_holder:
            return {'success': False, 'error': 'No current holder', 'channel': None}

        subject = f"Deadline approaching: File {file.file_number}"
        message = (
            f"File '{file.title}' ({file.file_number}) deadline is in {hours_remaining} hours.\n"
            f"Due date: {file.due_date}\n"
            f"Priority: {file.get_priority_display()}"
        )
        return NotificationService.send_notification(
            recipient=file.current_holder, subject=subject, message=message,
            file=file, notification_type='DEADLINE_REMINDER',
            priority='HIGH'
        )

    @staticmethod
    def notify_file_recalled(*, file, recalled_by, recipient) -> dict:
        """Send notification when file is recalled."""
        subject = f"File {file.file_number} recalled"
        message = (
            f"File '{file.title}' ({file.file_number}) has been recalled by "
            f"{recalled_by.get_full_name() or recalled_by.username}.\n"
            f"Please return the file immediately."
        )
        return NotificationService.send_notification(
            recipient=recipient, subject=subject, message=message,
            file=file, notification_type='FILE_RECALL',
            priority='HIGH'
        )

    @staticmethod
    def get_user_notifications(user, unread_only=False, limit=50) -> list:
        """Get notifications for a user."""
        try:
            from apps.communication.models import UserNotification
            qs = UserNotification.objects.filter(user=user)
            if unread_only:
                qs = qs.filter(is_read=False)
            return list(qs.order_by('-created_at')[:limit])
        except ImportError:
            logger.warning("UserNotification model not available")
            return []
        except Exception as e:
            logger.error(f"Error fetching notifications for {user}: {e}")
            return []

    @staticmethod
    def mark_notification_read(notification_id, user) -> bool:
        """Mark a notification as read."""
        try:
            from apps.communication.models import UserNotification
            notif = UserNotification.objects.get(id=notification_id, user=user)
            notif.is_read = True
            notif.read_at = timezone.now()
            notif.save(update_fields=['is_read', 'read_at'])
            return True
        except ImportError:
            logger.warning("UserNotification model not available")
            return False
        except Exception as e:
            logger.error(f"Error marking notification {notification_id} as read: {e}")
            return False
