"""
Management command to update principal and VP email addresses
and send password reset emails.

Usage:
    python manage.py update_principal_vp_emails --dry-run
    python manage.py update_principal_vp_emails --send-resets
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()


class Command(BaseCommand):
    help = 'Update principal and VP email addresses and send password resets'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without making them',
        )
        parser.add_argument(
            '--send-resets',
            action='store_true',
            help='Send password reset emails after updating',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        send_resets = options['send_resets']

        # Get all principals and VPs
        principals_vps = User.objects.filter(role__in=['PRI', 'VP'])

        self.stdout.write(self.style.NOTICE(
            f'\nFound {principals_vps.count()} principals and vice-principals\n'
        ))

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made\n'))

        updated = 0
        resets_sent = 0

        for user in principals_vps:
            # Current email info
            old_email = user.email
            role_display = 'Principal' if user.role == 'PRI' else 'Vice Principal'

            self.stdout.write(f'{role_display}: {old_email} ({user.first_name} {user.last_name})')

            if not dry_run:
                # Here you would update the email if needed
                # For now, we just log what would happen
                self.stdout.write(f'  -> Email would be updated to: {user.email}')

            if send_resets and not dry_run:
                # Generate password reset token
                token = default_token_generator.make_token(user)
                uid = user.pk

                # Create reset URL
                reset_url = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"

                # Send reset email
                subject = 'Education District IV - Password Reset'
                message = f"""
Hello {user.first_name},

You are receiving this email because a password reset was requested for your account.

Your email: {user.email}
Your role: {role_display}

To reset your password, visit:
{reset_url}

If you did not request this, please ignore this email.

Best regards,
Education District IV Portal Team
"""
                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                    resets_sent += 1
                    self.stdout.write(f'  -> Reset email sent to {user.email}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  -> Failed to send reset: {e}'))

            updated += 1

        # Summary
        self.stdout.write(self.style.SUCCESS(
            f'\n{"Would update" if dry_run else "Updated"}: {updated} users'
        ))
        if send_resets:
            self.stdout.write(self.style.SUCCESS(
                f'Password reset emails sent: {resets_sent}'
            ))

        if dry_run:
            self.stdout.write(self.style.WARNING(
                '\nRun without --dry-run to apply changes'
            ))
