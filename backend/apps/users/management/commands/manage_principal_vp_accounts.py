"""
Management command to manage principal and VP accounts.
Lists, updates emails, and sends password resets.

Usage:
    python manage.py manage_principal_vp_accounts --list
    python manage.py manage_principal_vp_accounts --update-emails
    python manage.py manage_principal_vp_accounts --send-resets
"""
import csv
import sys
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from apps.schools.models import School

User = get_user_model()


class Command(BaseCommand):
    help = 'Manage principal and vice-principal accounts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all principals and VPs with school info',
        )
        parser.add_argument(
            '--update-emails',
            action='store_true',
            help='Update email addresses to new format',
        )
        parser.add_argument(
            '--send-resets',
            action='store_true',
            help='Send password reset emails',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without making them',
        )

    def handle(self, *args, **options):
        list_only = options['list']
        update_emails = options['update_emails']
        send_resets = options['send_resets']
        dry_run = options['dry_run']

        # If no action specified, default to list
        if not (list_only or update_emails or send_resets):
            list_only = True

        # Get all principals and VPs with school info
        schools = School.objects.select_related('principal', 'vice_principal').all()
        
        principals = []
        vice_principals = []
        
        for school in schools:
            if school.principal:
                principals.append({
                    'user': school.principal,
                    'school': school,
                    'type': 'Principal'
                })
            if school.vice_principal:
                vice_principals.append({
                    'user': school.vice_principal,
                    'school': school,
                    'type': 'Vice Principal'
                })

        all_users = principals + vice_principals

        if list_only:
            self.stdout.write(self.style.NOTICE('\n=== Principals and Vice-Principals ===\n'))
            self.stdout.write(f'{"Email":<45} {"Role":<20} {"Name":<30} {"School Code":<15} {"Active"}')
            self.stdout.write('-' * 130)

            for item in all_users:
                user = item['user']
                school = item['school']
                role_display = item['type']
                full_name = f'{user.first_name} {user.last_name}'
                active = 'Yes' if user.is_active else 'No'
                
                self.stdout.write(
                    f'{user.email:<45} {role_display:<20} {full_name:<30} {school.code:<15} {active}'
                )

            self.stdout.write(self.style.SUCCESS(f'\nTotal: {len(all_users)} users'))
            return

        if update_emails:
            self.stdout.write(self.style.NOTICE('\n=== Updating Email Addresses ===\n'))
            updated = 0
            
            for item in all_users:
                user = item['user']
                school = item['school']
                old_email = user.email
                
                # Generate new email based on role and school code
                if user.role == 'PRI':
                    new_email = f'principal_{school.code.lower()}@ediv.gov.ng'
                else:
                    new_email = f'vp_{school.code.lower()}@ediv.gov.ng'
                
                self.stdout.write(f'{user.first_name} {user.last_name}: {old_email} -> {new_email}')
                
                if not dry_run and old_email != new_email:
                    # Check if new email already exists
                    if User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
                        self.stdout.write(self.style.WARNING(f'  -> Skipped: {new_email} already exists'))
                    else:
                        user.email = new_email
                        user.save(update_fields=['email'])
                        updated += 1
                        self.stdout.write(f'  -> Updated')
                
            self.stdout.write(self.style.SUCCESS(
                f'\n{"Would update" if dry_run else "Updated"}: {updated} email addresses'
            ))

        if send_resets:
            self.stdout.write(self.style.NOTICE('\n=== Sending Password Reset Emails ===\n'))
            resets_sent = 0
            
            for item in all_users:
                user = item['user']
                role_display = item['type']
                
                # Generate password reset token
                token = default_token_generator.make_token(user)
                uid = user.pk
                
                # Create reset URL
                frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
                reset_url = f"{frontend_url}/reset-password?uid={uid}&token={token}"
                
                # Send reset email
                subject = 'Education District IV - Password Reset'
                message = f"""
Hello {user.first_name},

You are receiving this email because a password reset was requested for your account.

Your email: {user.email}
Your role: {role_display}
Your school: {item['school'].name}

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
                    self.stdout.write(f'  -> Sent to {user.email}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  -> Failed to send to {user.email}: {e}'))
            
            self.stdout.write(self.style.SUCCESS(f'\nPassword reset emails sent: {resets_sent}'))
