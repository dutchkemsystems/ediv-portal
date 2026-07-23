from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Ensure admin user exists for login testing'

    def handle(self, *args, **options):
        email = 'admin@ediv.gov.ng'
        password = 'Admin@12345678'

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': 'SYSADMIN',
                'phone_number': '+2348010000001',
                'is_staff': True,
                'is_superuser': True,
            },
        )
        user.set_password(password)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.role = 'SYSADMIN'
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f'Created admin user: {email}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Updated admin user: {email}'))

        # Also ensure TG user exists
        tg_email = 'tg@ediv.gov.ng'
        tg, tg_created = User.objects.get_or_create(
            email=tg_email,
            defaults={
                'first_name': 'Abimbola',
                'last_name': 'Adesanya',
                'role': 'TG',
                'phone_number': '+2348010000002',
                'is_staff': True,
            },
        )
        tg.set_password('TutorGen@12345')
        tg.is_active = True
        tg.save()

        if tg_created:
            self.stdout.write(self.style.SUCCESS(f'Created TG user: {tg_email}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Updated TG user: {tg_email}'))

        self.stdout.write(self.style.SUCCESS(f'\nTotal users: {User.objects.count()}'))
