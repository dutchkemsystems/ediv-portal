"""
Integration between mail_workflow and communication apps.
When mail status changes, create in-app notifications and optionally send emails.
"""

import logging

from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


def notify_mail_status_change(mail, old_status, new_status, changed_by=None):
    """Create in-app notification when mail status changes."""
    try:
        from apps.communication.models import UserNotification

        # Determine recipients based on mail type
        recipients = set()

        # Notify the person who created/received the mail
        if hasattr(mail, "received_by") and mail.received_by:
            recipients.add(mail.received_by)

        # Notify assigned person
        if hasattr(mail, "assigned_to") and mail.assigned_to:
            recipients.add(mail.assigned_to)

        # Notify current holder
        if hasattr(mail, "current_holder") and mail.current_holder:
            recipients.add(mail.current_holder)

        # Notify creator (for outgoing mail)
        if hasattr(mail, "created_by") and mail.created_by:
            recipients.add(mail.created_by)

        # Notify sender/recipient for correspondence
        if hasattr(mail, "sender") and mail.sender:
            recipients.add(mail.sender)
        if hasattr(mail, "recipient") and mail.recipient:
            recipients.add(mail.recipient)

        # Remove the person who made the change
        if changed_by:
            recipients.discard(changed_by)

        # Create notifications
        mail_type = mail.__class__.__name__
        ref_number = getattr(mail, "mail_number", None) or getattr(mail, "reference_number", "Unknown")

        for recipient in recipients:
            if recipient and recipient.is_active:
                UserNotification.objects.create(
                    user=recipient,
                    notification_type="INFO",
                    title=f"{mail_type} Status Update",
                    message=f"{ref_number} status changed from {old_status} to {new_status}",
                    link=f"/mail-workflow",
                )

        logger.info(f"Mail notifications sent for {ref_number}: {old_status} -> {new_status}")

    except Exception as e:
        logger.warning(f"Failed to create mail notifications: {e}")


def notify_mail_assigned(mail, assigned_to, assigned_by=None):
    """Create in-app notification when mail is assigned."""
    try:
        from apps.communication.models import UserNotification

        if assigned_to and assigned_to.is_active:
            ref_number = getattr(mail, "mail_number", None) or getattr(mail, "reference_number", "Unknown")
            UserNotification.objects.create(
                user=assigned_to,
                notification_type="INFO",
                title="Mail Assignment",
                message=f"You have been assigned {ref_number}: {mail.subject}",
                link="/mail-workflow",
            )

        logger.info(f"Assignment notification sent for {ref_number}")

    except Exception as e:
        logger.warning(f"Failed to create assignment notification: {e}")


def notify_file_movement(file, from_holder, to_holder, action, moved_by=None):
    """Create in-app notification when a file moves between holders."""
    try:
        from apps.communication.models import UserNotification

        recipients = set()
        if to_holder:
            recipients.add(to_holder)
        if from_holder and from_holder != moved_by:
            recipients.add(from_holder)

        if moved_by:
            recipients.discard(moved_by)

        for recipient in recipients:
            if recipient and recipient.is_active:
                UserNotification.objects.create(
                    user=recipient,
                    notification_type="INFO",
                    title="File Movement",
                    message=f"File {file.file_number} ({file.title}) - {action}",
                    link="/files",
                )

        logger.info(f"File movement notifications sent for {file.file_number}")

    except Exception as e:
        logger.warning(f"Failed to create file movement notifications: {e}")
