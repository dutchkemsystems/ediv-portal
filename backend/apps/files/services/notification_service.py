"""Enhanced Multi-Channel Notification Service for file movements."""
import logging
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

User = get_user_model()
logger = logging.getLogger(__name__)


class NotificationService:
    """Enhanced multi-channel notification service with email/SMS support."""

    CHANNEL_CHOICES = ['email', 'sms', 'whatsapp', 'in_app']

    @staticmethod
    def send_notification(*, recipient, subject, message, channel='in_app',
                         file=None, notification_type='FILE_MOVEMENT',
                         priority='NORMAL', metadata=None) -> dict:
        """
        Send a notification through specified channel.
        Returns: {'success': bool, 'channel': str, 'error': str or None}
        """
        if channel not in NotificationService.CHANNEL_CHOICES:
            return {
                'success': False,
                'channel': channel,
                'error': f'Invalid channel: {channel}',
            }

        try:
            if channel == 'in_app':
                from apps.communication.models import UserNotification
                notif_type = 'INFO'
                if priority in ('HIGH', 'URGENT'):
                    notif_type = 'WARNING'
                if notification_type == 'FILE_ESCALATION':
                    notif_type = 'ERROR'
                UserNotification.objects.create(
                    user=recipient,
                    title=subject,
                    message=message,
                    notification_type=notif_type,
                    is_read=False,
                )
                logger.info(f"In-app notification sent to {recipient}: {subject}")

            elif channel == 'email':
                NotificationService._send_email(recipient, subject, message)

            elif channel == 'sms':
                NotificationService._send_sms(recipient, subject, message)

            elif channel == 'whatsapp':
                NotificationService._send_whatsapp(recipient, subject, message)

            return {'success': True, 'channel': channel, 'error': None}

        except Exception as e:
            logger.error(f"Failed to send {channel} notification to {recipient}: {e}")
            return {'success': False, 'channel': channel, 'error': str(e)}

    @staticmethod
    def _send_email(recipient, subject, message):
        """Send email notification."""
        email_from = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@edivportal.gov.ng')
        html_message = None

        try:
            html_message = render_to_string('emails/notification.html', {
                'user': recipient,
                'title': subject,
                'message': message,
                'year': timezone.now().year,
            })
        except Exception:
            pass

        plain_message = strip_tags(html_message) if html_message else message

        send_mail(
            subject=f'[{subject}] - Education District IV Portal',
            message=plain_message,
            from_email=email_from,
            recipient_list=[recipient.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Email sent to {recipient.email}: {subject}")

    @staticmethod
    def _send_sms(recipient, subject, message):
        """Send SMS notification via Twilio if configured."""
        account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
        auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
        from_number = getattr(settings, 'TWILIO_PHONE_NUMBER', '')

        if not all([account_sid, auth_token, from_number]):
            logger.info(f"[SMS] Twilio not configured. To: {recipient.phone_number} | {subject}: {message[:100]}")
            return

        try:
            from twilio.rest import Client
            client = Client(account_sid, auth_token)
            sms_body = f"{subject}\n{message[:140]}"
            client.messages.create(
                body=sms_body,
                from_=from_number,
                to=recipient.phone_number,
            )
            logger.info(f"SMS sent to {recipient.phone_number}: {subject}")
        except ImportError:
            logger.warning("Twilio library not installed. SMS not sent.")
        except Exception as e:
            logger.error(f"SMS send failed: {e}")

    @staticmethod
    def _send_whatsapp(recipient, subject, message):
        """Send WhatsApp notification via Twilio if configured."""
        account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
        auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
        whatsapp_number = getattr(settings, 'WHATSAPP_PHONE_NUMBER', '')

        if not all([account_sid, auth_token, whatsapp_number]):
            logger.info(f"[WHATSAPP] Not configured. To: {recipient.phone_number} | {subject}")
            return

        try:
            from twilio.rest import Client
            client = Client(account_sid, auth_token)
            wa_body = f"*{subject}*\n\n{message[:200]}"
            client.messages.create(
                body=wa_body,
                from_=f'whatsapp:{whatsapp_number}',
                to=f'whatsapp:{recipient.phone_number}',
            )
            logger.info(f"WhatsApp sent to {recipient.phone_number}: {subject}")
        except ImportError:
            logger.warning("Twilio library not installed. WhatsApp not sent.")
        except Exception as e:
            logger.error(f"WhatsApp send failed: {e}")

    @staticmethod
    def send_multi_channel(*, recipient, subject, message, channels=None,
                          file=None, notification_type='FILE_MOVEMENT',
                          priority='NORMAL') -> list:
        """Send notification via multiple channels."""
        if channels is None:
            channels = ['in_app', 'email']

        results = []
        for channel in channels:
            result = NotificationService.send_notification(
                recipient=recipient,
                subject=subject,
                message=message,
                channel=channel,
                file=file,
                notification_type=notification_type,
                priority=priority,
            )
            results.append(result)
        return results

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
    def notify_workflow_advanced(*, file, from_user, to_user, step_info) -> dict:
        """Send notification when file advances in workflow."""
        subject = f"File {file.file_number} - Step {step_info.get('step', '?')}: {step_info.get('label', '')}"
        message = (
            f"File '{file.title}' ({file.file_number}) has advanced to:\n"
            f"Step {step_info.get('step')}: {step_info.get('label', '')}\n"
            f"From: {from_user.get_full_name() or from_user.username}\n"
            f"Action required by: {step_info.get('role', 'N/A')}"
        )
        return NotificationService.send_notification(
            recipient=to_user, subject=subject, message=message,
            file=file, notification_type='FILE_MOVEMENT',
            priority=file.priority
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
        except Exception as e:
            logger.error(f"Error marking notification {notification_id} as read: {e}")
            return False
