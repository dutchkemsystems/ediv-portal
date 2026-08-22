"""
Celery tasks for email notifications and automation.
"""
import logging
from datetime import timedelta

from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_notification(self, subject, message, recipient_list, html_message=None):
    """Send an email notification asynchronously."""
    try:
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@ediv.gov.ng")
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Email sent to {recipient_list}: {subject}")
        return {"status": "sent", "recipients": recipient_list}
    except Exception as exc:
        logger.error(f"Email failed to {recipient_list}: {exc}")
        self.retry(exc=exc)


@shared_task
def send_mail_assignment_notification(assignment_id):
    """Send email when mail is assigned to a staff member."""
    try:
        from apps.mail_workflow.models import MailAssignment
        assignment = MailAssignment.objects.select_related(
            "incoming_mail", "assigned_to", "assigned_by"
        ).get(id=assignment_id)

        mail = assignment.incoming_mail
        user = assignment.assigned_to

        context = {
            "user_name": user.get_full_name() or user.email,
            "title": "Mail Assignment Notification",
            "message": f"You have been assigned a mail for action. Reference: {mail.mail_number}",
            "mail_number": mail.mail_number,
            "mail_subject": mail.subject,
            "mail_from": mail.sender_name,
            "mail_priority": mail.priority,
            "deadline": assignment.deadline.strftime("%d %B %Y %H:%M") if assignment.deadline else None,
            "action_required": assignment.action_required,
            "action_url": f"{getattr(settings, 'FRONTEND_URL', 'https://ediv-portal.onrender.com')}/mail-workflow",
            "year": timezone.now().year,
        }

        html_content = render_to_string("emails/mail_notification.html", context)

        send_email_notification.delay(
            subject=f"Mail Assignment: {mail.subject}",
            message=f"You have been assigned mail {mail.mail_number} for action.",
            recipient_list=[user.email],
            html_message=html_content,
        )
    except Exception as exc:
        logger.error(f"Mail assignment notification failed: {exc}")


@shared_task
def send_mail_status_change_notification(mail_id, old_status, new_status, changed_by_id):
    """Send email when mail status changes."""
    try:
        from apps.mail_workflow.models import IncomingMail
        from apps.users.models import User

        mail = IncomingMail.objects.get(id=mail_id)
        changed_by = User.objects.get(id=changed_by_id)

        # Notify all people involved in the mail workflow
        recipients = set()
        if mail.created_by and mail.created_by.email:
            recipients.add(mail.created_by.email)

        # Notify assigned staff
        from apps.mail_workflow.models import MailAssignment
        assignments = MailAssignment.objects.filter(incoming_mail=mail).select_related("assigned_to")
        for a in assignments:
            if a.assigned_to and a.assigned_to.email:
                recipients.add(a.assigned_to.email)

        if not recipients:
            return

        context = {
            "user_name": "Team Member",
            "title": "Mail Status Update",
            "message": f"Mail {mail.mail_number} status changed from {old_status} to {new_status} by {changed_by.get_full_name()}.",
            "mail_number": mail.mail_number,
            "mail_subject": mail.subject,
            "action_url": f"{getattr(settings, 'FRONTEND_URL', 'https://ediv-portal.onrender.com')}/mail-workflow",
            "year": timezone.now().year,
        }

        html_content = render_to_string("emails/mail_notification.html", context)

        send_email_notification.delay(
            subject=f"Mail Status Changed: {mail.mail_number} - {new_status}",
            message=context["message"],
            recipient_list=list(recipients),
            html_message=html_content,
        )
    except Exception as exc:
        logger.error(f"Mail status notification failed: {exc}")


@shared_task
def send_file_movement_notification(file_id, to_holder_id, action, remarks=""):
    """Send email when a file is moved to a new holder."""
    try:
        from apps.files.models import File
        from apps.users.models import User

        file_obj = File.objects.get(id=file_id)
        to_holder = User.objects.get(id=to_holder_id)

        context = {
            "user_name": to_holder.get_full_name() or to_holder.email,
            "title": "File Assignment Notification",
            "message": f"A file has been assigned to you. File Number: {file_obj.file_number}",
            "details": f"Title: {file_obj.title}\nAction: {action}\nRemarks: {remarks}",
            "action_url": f"{getattr(settings, 'FRONTEND_URL', 'https://ediv-portal.onrender.com')}/files",
            "year": timezone.now().year,
        }

        html_content = render_to_string("emails/notification.html", context)

        send_email_notification.delay(
            subject=f"File Assigned: {file_obj.file_number}",
            message=context["message"],
            recipient_list=[to_holder.email],
            html_message=html_content,
        )
    except Exception as exc:
        logger.error(f"File movement notification failed: {exc}")


@shared_task
def check_overdue_mails():
    """Periodic task to check for overdue mail assignments and send reminders."""
    try:
        from apps.mail_workflow.models import MailAssignment

        overdue = MailAssignment.objects.filter(
            deadline__lt=timezone.now(),
            status__in=["PENDING", "IN_PROGRESS"],
        ).select_related("incoming_mail", "assigned_to")

        for assignment in overdue:
            if assignment.assigned_to and assignment.assigned_to.email:
                context = {
                    "user_name": assignment.assigned_to.get_full_name() or assignment.assigned_to.email,
                    "title": "Overdue Mail Reminder",
                    "message": f"Mail {assignment.incoming_mail.mail_number} is overdue. Please take action immediately.",
                    "mail_number": assignment.incoming_mail.mail_number,
                    "mail_subject": assignment.incoming_mail.subject,
                    "deadline": assignment.deadline.strftime("%d %B %Y %H:%M"),
                    "action_url": f"{getattr(settings, 'FRONTEND_URL', 'https://ediv-portal.onrender.com')}/mail-workflow",
                    "year": timezone.now().year,
                }

                html_content = render_to_string("emails/mail_notification.html", context)

                send_email_notification.delay(
                    subject=f"OVERDUE: Mail {assignment.incoming_mail.mail_number}",
                    message=context["message"],
                    recipient_list=[assignment.assigned_to.email],
                    html_message=html_content,
                )
    except Exception as exc:
        logger.error(f"Overdue mail check failed: {exc}")


@shared_task
def check_overdue_files():
    """Periodic task to check for overdue files and escalate."""
    try:
        from apps.files.models import File
        from apps.files.services.file_movement_service import FileMovementService

        overdue_files = File.objects.filter(
            expected_completion__lt=timezone.now(),
            status__in=["ACTIVE", "IN_WORKFLOW"],
            is_overdue=False,
        )

        for file_obj in overdue_files:
            try:
                FileMovementService.escalate_file(
                    file_id=file_obj.id,
                    escalated_by_id=file_obj.current_holder_id or file_obj.created_by_id,
                    remarks="Auto-escalated: overdue file"
                )
            except Exception as exc:
                logger.error(f"Auto-escalate file {file_obj.id} failed: {exc}")
    except Exception as exc:
        logger.error(f"Overdue file check failed: {exc}")


@shared_task
def send_weekly_digest():
    """Send weekly digest email to department heads."""
    try:
        from apps.users.models import User
        from apps.files.models import File
        from apps.mail_workflow.models import IncomingMail

        week_ago = timezone.now() - timedelta(days=7)

        dept_heads = User.objects.filter(
            role__in=["SYSADMIN", "TG_PS", "HR", "FIN", "AUDIT", "QA", "REG", "SA"]
        ).exclude(email="")

        for user in dept_heads:
            files_received = File.objects.filter(
                current_holder=user, created_at__gte=week_ago
            ).count()

            mails_assigned = IncomingMail.objects.filter(
                mailassignment__assigned_to=user,
                created_at__gte=week_ago
            ).count()

            if files_received == 0 and mails_assigned == 0:
                continue

            context = {
                "user_name": user.get_full_name() or user.email,
                "title": "Weekly Activity Digest",
                "message": f"Here is your weekly activity summary for Education District IV Portal.",
                "details": f"Files received this week: {files_received}\nMails assigned this week: {mails_assigned}",
                "action_url": f"{getattr(settings, 'FRONTEND_URL', 'https://ediv-portal.onrender.com')}/dashboard",
                "year": timezone.now().year,
            }

            html_content = render_to_string("emails/notification.html", context)

            send_email_notification.delay(
                subject="Weekly Activity Digest - Education District IV",
                message=f"Files: {files_received}, Mails: {mails_assigned}",
                recipient_list=[user.email],
                html_message=html_content,
            )
    except Exception as exc:
        logger.error(f"Weekly digest failed: {exc}")
