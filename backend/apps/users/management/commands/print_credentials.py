from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Print all user login credentials in a formatted table'

    def handle(self, *args, **options):
        passwords = {
            'SYSADMIN': os.environ.get('ADMIN_PASSWORD', '*** NOT SET ***'),
            'TG': os.environ.get('TG_PASSWORD', '*** NOT SET ***'),
        }
        dept_head_pw = os.environ.get('HEAD_OFFICE_PASSWORD', '*** NOT SET ***')
        school_staff_pw = os.environ.get('SCHOOL_STAFF_PASSWORD', '*** NOT SET ***')
        teacher_pw = os.environ.get('TEACHER_PASSWORD', '*** NOT SET ***')
        student_pw = os.environ.get('STUDENT_PASSWORD', '*** NOT SET ***')

        users = User.objects.all().order_by('role', 'email')

        # Group by role
        by_role = {}
        for u in users:
            by_role.setdefault(u.role, []).append(u)

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 100))
        self.stdout.write(self.style.SUCCESS('EDUCATION DISTRICT IV PORTAL — ALL LOGIN CREDENTIALS'))
        self.stdout.write(self.style.SUCCESS('=' * 100))

        # --- Admin Users ---
        self.stdout.write(self.style.NOTICE('\n--- ADMIN & TUTOR GENERAL ---'))
        self.stdout.write(f'{"Email":<40} {"Name":<30} {"Role":<10} {"Password"}')
        self.stdout.write('-' * 100)
        for role in ['SYSADMIN', 'TG']:
            for u in by_role.get(role, []):
                pw = passwords.get(role, '???')
                self.stdout.write(f'{u.email:<40} {u.get_full_name():<30} {u.role:<10} {pw}')

        # --- Department Heads ---
        self.stdout.write(self.style.NOTICE('\n--- DEPARTMENT HEADS ---'))
        self.stdout.write(f'{"Email":<35} {"Name":<25} {"Role":<8} {"Dept Code":<12} {"Password"}')
        self.stdout.write('-' * 100)
        dept_roles = ['HR', 'FIN', 'QA', 'CC', 'SA', 'REG', 'FRENCH']
        dept_codes = {
            'HR': 'ADMIN_HR', 'FIN': 'FIN', 'QA': 'QA', 'CC': 'CC',
            'SA': 'SA', 'REG': 'REG', 'FRENCH': 'FRENCH',
        }
        for role in dept_roles:
            for u in by_role.get(role, []):
                code = dept_codes.get(role, role)
                self.stdout.write(f'{u.email:<35} {u.get_full_name():<25} {u.role:<8} {code:<12} {dept_head_pw}')

        # --- Major Unit Heads ---
        self.stdout.write(self.style.NOTICE('\n--- MAJOR UNIT HEADS (District HQ) ---'))
        self.stdout.write(f'{"Email":<35} {"Name":<25} {"Role":<8} {"Unit Code":<12} {"Password"}')
        self.stdout.write('-' * 100)
        unit_roles = ['AUDIT', 'EMIS', 'PLAN', 'PROC', 'PA']
        for role in unit_roles:
            for u in by_role.get(role, []):
                self.stdout.write(f'{u.email:<35} {u.get_full_name():<25} {u.role:<8} {role:<12} {dept_head_pw}')

        # --- Principals ---
        principals = by_role.get('PRI', [])
        self.stdout.write(self.style.NOTICE(f'\n--- PRINCIPALS ({len(principals)} total) ---'))
        self.stdout.write(f'{"Email":<45} {"Name":<25} {"Password"}')
        self.stdout.write('-' * 90)
        for u in principals:
            self.stdout.write(f'{u.email:<45} {u.get_full_name():<25} {school_staff_pw}')

        # --- Vice Principals ---
        vps = by_role.get('VP', [])
        self.stdout.write(self.style.NOTICE(f'\n--- VICE PRINCIPALS ({len(vps)} total) ---'))
        self.stdout.write(f'{"Email":<45} {"Name":<25} {"Password"}')
        self.stdout.write('-' * 90)
        for u in vps:
            self.stdout.write(f'{u.email:<45} {u.get_full_name():<25} {school_staff_pw}')

        # --- Teachers ---
        teachers = by_role.get('TCH', [])
        self.stdout.write(self.style.NOTICE(f'\n--- TEACHERS ({len(teachers)} total) ---'))
        self.stdout.write(f'{"Email":<40} {"Name":<30} {"Password"}')
        self.stdout.write('-' * 90)
        for u in teachers[:20]:
            self.stdout.write(f'{u.email:<40} {u.get_full_name():<30} {teacher_pw}')
        if len(teachers) > 20:
            self.stdout.write(f'  ... and {len(teachers) - 20} more teachers')

        # --- Summary ---
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 100))
        self.stdout.write(self.style.SUCCESS('SUMMARY'))
        self.stdout.write(self.style.SUCCESS('=' * 100))
        self.stdout.write(f'  Total users: {users.count()}')
        for role in sorted(by_role.keys()):
            self.stdout.write(f'    {role:<12}: {len(by_role[role])}')

        self.stdout.write(self.style.SUCCESS(f'\nPassword Reference (from env vars):'))
        self.stdout.write(f'  SYSADMIN:        {os.environ.get("ADMIN_PASSWORD", "*** NOT SET ***")}')
        self.stdout.write(f'  TG:              {os.environ.get("TG_PASSWORD", "*** NOT SET ***")}')
        self.stdout.write(f'  Dept/Unit Heads: {os.environ.get("HEAD_OFFICE_PASSWORD", "*** NOT SET ***")}')
        self.stdout.write(f'  Principals/VPs:  {os.environ.get("SCHOOL_STAFF_PASSWORD", "*** NOT SET ***")}')
        self.stdout.write(f'  Teachers:        {os.environ.get("TEACHER_PASSWORD", "*** NOT SET ***")}')
        self.stdout.write(f'  Students:        {os.environ.get("STUDENT_PASSWORD", "*** NOT SET ***")}')
