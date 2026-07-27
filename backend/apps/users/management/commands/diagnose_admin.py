"""
Diagnose and unlock the admin user.

Usage:
    python manage.py diagnose_admin           # Show admin status
    python manage.py diagnose_admin --unlock  # Clear lockout + reset password
    python manage.py diagnose_admin --unlock --email admin@ediv.gov.ng --password Admin@12345678
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import authenticate
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Diagnose admin account status and optionally unlock it.'

    def add_arguments(self, parser):
        parser.add_argument('--unlock', action='store_true', help='Clear lockout and reset password')
        parser.add_argument('--email', default='admin@ediv.gov.ng', help='Admin email')
        parser.add_argument('--password', default='Admin@12345678', help='New password to set')

    def handle(self, *args, **options):
        from apps.users.models import User

        email = options['email']
        unlock = options['unlock']
        password = options['password']

        self.stdout.write('=' * 60)
        self.stdout.write('ADMIN DIAGNOSTIC')
        self.stdout.write('=' * 60)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'USER NOT FOUND: {email}'))
            self.stdout.write('Run: python manage.py ensure_admin first')
            return

        self.stdout.write(f'Email:           {user.email}')
        self.stdout.write(f'Role:            {user.role}')
        self.stdout.write(f'is_active:       {user.is_active}')
        self.stdout.write(f'is_staff:        {user.is_staff}')
        self.stdout.write(f'is_superuser:    {user.is_superuser}')
        self.stdout.write(f'failed_attempts: {user.failed_login_attempts}')
        self.stdout.write(f'locked_until:    {user.locked_until}')
        self.stdout.write(f'mfa_enabled:     {user.mfa_enabled}')
        self.stdout.write(f'last_login:      {user.last_login}')

        # Test password
        test_ok = user.check_password(password)
        self.stdout.write(f'password_check:  {"OK" if test_ok else "MISMATCH"} ({password})')

        # Test authenticate()
        auth_result = authenticate(email=email, password=password)
        self.stdout.write(f'authenticate():  {"OK" if auth_result else "FAILED"}')

        # Check cache lockout
        cache_key = f'ediv:lockout:{user.id}'
        lockout_data = cache.get(cache_key)
        self.stdout.write(f'cache_lockout:   {lockout_data if lockout_data else "NONE"}')

        self.stdout.write('')

        if not unlock:
            self.stdout.write('Re-run with --unlock to clear lockout and reset password.')
            return

        # Unlock
        self.stdout.write(self.style.WARNING('UNLOCKING...'))

        user.failed_login_attempts = 0
        user.locked_until = None
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.mfa_enabled = False
        user.set_password(password)
        user.save()

        cache.delete(cache_key)
        cache.delete_pattern('ediv:lockout:*') if hasattr(cache, 'delete_pattern') else None

        self.stdout.write(self.style.SUCCESS(f'Admin unlocked.'))
        self.stdout.write(self.style.SUCCESS(f'  Email:    {email}'))
        self.stdout.write(self.style.SUCCESS(f'  Password: {password}'))

        # Verify
        user.refresh_from_db()
        auth_result = authenticate(email=email, password=password)
        self.stdout.write(f'Verify authenticate(): {"OK" if auth_result else "FAILED"}')
