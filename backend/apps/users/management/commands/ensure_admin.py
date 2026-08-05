import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


def _upsert(email, password, **kwargs):
    user, created = User.objects.get_or_create(
        email=email,
        defaults=kwargs,
    )
    user.set_password(password)
    user.is_active = True
    for k, v in kwargs.items():
        if k not in ('first_name', 'last_name', 'role', 'phone_number'):
            setattr(user, k, v)
    user.save()
    return user, created


class Command(BaseCommand):
    help = 'Ensure essential admin/head-office users exist with correct passwords'

    def handle(self, *args, **options):
        admin_pw = os.environ.get('ADMIN_PASSWORD') or 'Admin@12345678'
        tg_pw = os.environ.get('TG_PASSWORD') or 'TutorGen@12345'
        head_pw = os.environ.get('HEAD_OFFICE_PASSWORD') or 'HeadOffice@123'

        essential_users = [
            ('admin@ediv.gov.ng', admin_pw, 'System', 'Administrator', 'SYSADMIN', '+2348010000001', True, True),
            ('tg.ps@ediv.gov.ng', tg_pw, 'Abimbola', 'Adesanya', 'TG_PS', '+2348010000002', True, False),
            ('tg@ediv.gov.ng', tg_pw, 'Abimbola', 'Adesanya', 'TG_PS', '+2348010000002', True, False),
            ('hr.head@ediv.gov.ng', head_pw, 'Funmilayo', 'Ogundimu', 'HR', '+2348010000003', True, False),
            ('finance.head@ediv.gov.ng', head_pw, 'Adewale', 'Bakare', 'FIN', '+2348010000004', True, False),
            ('qa.head@ediv.gov.ng', head_pw, 'Oluwaseun', 'Ajayi', 'QA', '+2348010000005', True, False),
            ('cc.head@ediv.gov.ng', head_pw, 'Chinedu', 'Eze', 'CC', '+2348010000006', True, False),
            ('sa.head@ediv.gov.ng', head_pw, 'Adewale', 'Lawal', 'SA', '+2348010000007', True, False),
            ('registry.head@ediv.gov.ng', head_pw, 'Folake', 'Okafor', 'REG', '+2348010000008', True, False),
            ('spd.head@ediv.gov.ng', head_pw, 'Ibrahim', 'Abubakar', 'SA', '+2348010000009', True, False),
            ('sss.head@ediv.gov.ng', head_pw, 'Ngozi', 'Nwosu', 'QA', '+2348010000010', True, False),
            ('french.head@ediv.gov.ng', head_pw, 'Amina', 'Mohammed', 'FRENCH', '+2348010000011', True, False),
            ('audit.head@ediv.gov.ng', head_pw, 'Tunde', 'Fashola', 'AUDIT', '+2348010000012', True, False),
            ('emis.head@ediv.gov.ng', head_pw, 'Kolade', 'Akande', 'EMIS', '+2348010000013', True, False),
            ('plan.head@ediv.gov.ng', head_pw, 'Babatunde', 'Olumide', 'PLAN', '+2348010000014', True, False),
            ('procurement.head@ediv.gov.ng', head_pw, 'Emeka', 'Chukwu', 'PROC', '+2348010000015', True, False),
            ('pa.head@ediv.gov.ng', head_pw, 'Funke', 'Bakare', 'PA', '+2348010000016', True, False),
        ]

        created_count = 0
        updated_count = 0

        for email, password, first, last, role, phone, is_staff, is_super in essential_users:
            try:
                user, created = _upsert(
                    email=email,
                    password=password,
                    first_name=first,
                    last_name=last,
                    role=role,
                    phone_number=phone,
                    is_staff=is_staff,
                    is_superuser=is_super,
                )
                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'  + Created: {email} ({role})'))
                else:
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f'  ~ Updated: {email} ({role})'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ! Failed: {email} - {e}'))

        self.stdout.write(self.style.SUCCESS(
            f'\nDone: {created_count} created, {updated_count} updated, Total users: {User.objects.count()}'
        ))
