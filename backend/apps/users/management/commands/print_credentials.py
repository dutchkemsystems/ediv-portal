import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()

PASSWORD_ENV_MAP = {
    "SYSADMIN": "ADMIN_PASSWORD",
    "TG_PS": "TG_PASSWORD",
    "HR": "HEAD_OFFICE_PASSWORD",
    "FIN": "HEAD_OFFICE_PASSWORD",
    "AUDIT": "HEAD_OFFICE_PASSWORD",
    "QA": "HEAD_OFFICE_PASSWORD",
    "CC": "HEAD_OFFICE_PASSWORD",
    "EMIS": "HEAD_OFFICE_PASSWORD",
    "PLAN": "HEAD_OFFICE_PASSWORD",
    "PROC": "HEAD_OFFICE_PASSWORD",
    "PA": "HEAD_OFFICE_PASSWORD",
    "SA": "HEAD_OFFICE_PASSWORD",
    "FRENCH": "HEAD_OFFICE_PASSWORD",
    "REG": "HEAD_OFFICE_PASSWORD",
    "PRI": "SCHOOL_STAFF_PASSWORD",
    "VP": "SCHOOL_STAFF_PASSWORD",
    "TCH": "TEACHER_PASSWORD",
    "STD": "STUDENT_PASSWORD",
}

DEFAULT_PASSWORDS = {
    "ADMIN_PASSWORD": "Admin@12345678",
    "TG_PASSWORD": "TutorGen@12345",
    "HEAD_OFFICE_PASSWORD": "HeadOffice@123",
    "SCHOOL_STAFF_PASSWORD": "SchoolStaff@12345",
    "TEACHER_PASSWORD": "Teacher@12345",
    "STUDENT_PASSWORD": "Student@12345",
}


def _get_pw(role):
    env_key = PASSWORD_ENV_MAP.get(role)
    if env_key:
        return os.environ.get(env_key) or DEFAULT_PASSWORDS.get(env_key, "???")
    return "???"


class Command(BaseCommand):
    help = "Print all user login credentials organized by role"

    def handle(self, *args, **options):
        users = User.objects.all().order_by("role", "email")

        by_role = {}
        for u in users:
            by_role.setdefault(u.role, []).append(u)

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 110))
        self.stdout.write(self.style.SUCCESS("EDUCATION DISTRICT IV PORTAL — ALL LOGIN CREDENTIALS"))
        self.stdout.write(self.style.SUCCESS("=" * 110))

        # --- Admin Users ---
        self.stdout.write(self.style.NOTICE("\n--- ADMIN & TUTOR GENERAL ---"))
        self.stdout.write(f'{"Email":<40} {"Name":<30} {"Role":<10} {"Password"}')
        self.stdout.write("-" * 110)
        for role in ["SYSADMIN", "TG_PS"]:
            for u in by_role.get(role, []):
                self.stdout.write(f"{u.email:<40} {u.get_full_name():<30} {u.role:<10} {_get_pw(role)}")

        # --- Department Heads ---
        self.stdout.write(self.style.NOTICE("\n--- DEPARTMENT HEADS ---"))
        self.stdout.write(f'{"Email":<35} {"Name":<25} {"Role":<8} {"Password"}')
        self.stdout.write("-" * 110)
        for role in ["HR", "FIN", "QA", "CC", "SA", "REG", "FRENCH"]:
            for u in by_role.get(role, []):
                self.stdout.write(f"{u.email:<35} {u.get_full_name():<25} {u.role:<8} {_get_pw(role)}")

        # --- Major Unit Heads ---
        self.stdout.write(self.style.NOTICE("\n--- MAJOR UNIT HEADS ---"))
        self.stdout.write(f'{"Email":<35} {"Name":<25} {"Role":<8} {"Password"}')
        self.stdout.write("-" * 110)
        for role in ["AUDIT", "EMIS", "PLAN", "PROC", "PA"]:
            for u in by_role.get(role, []):
                self.stdout.write(f"{u.email:<35} {u.get_full_name():<25} {u.role:<8} {_get_pw(role)}")

        # --- Principals ---
        principals = by_role.get("PRI", [])
        self.stdout.write(self.style.NOTICE(f"\n--- PRINCIPALS ({len(principals)} total) ---"))
        self.stdout.write(f'{"Email":<45} {"Name":<25} {"Password"}')
        self.stdout.write("-" * 90)
        for u in principals[:20]:
            self.stdout.write(f"{u.email:<45} {u.get_full_name():<25} {_get_pw('PRI')}")
        if len(principals) > 20:
            self.stdout.write(f"  ... and {len(principals) - 20} more principals")

        # --- Vice Principals ---
        vps = by_role.get("VP", [])
        self.stdout.write(self.style.NOTICE(f"\n--- VICE PRINCIPALS ({len(vps)} total) ---"))
        self.stdout.write(f'{"Email":<45} {"Name":<25} {"Password"}')
        self.stdout.write("-" * 90)
        for u in vps[:20]:
            self.stdout.write(f"{u.email:<45} {u.get_full_name():<25} {_get_pw('VP')}")
        if len(vps) > 20:
            self.stdout.write(f"  ... and {len(vps) - 20} more vice principals")

        # --- Teachers ---
        teachers = by_role.get("TCH", [])
        self.stdout.write(self.style.NOTICE(f"\n--- TEACHERS ({len(teachers)} total) ---"))
        self.stdout.write(f'{"Email":<40} {"Name":<30} {"Password"}')
        self.stdout.write("-" * 90)
        for u in teachers[:20]:
            self.stdout.write(f"{u.email:<40} {u.get_full_name():<30} {_get_pw('TCH')}")
        if len(teachers) > 20:
            self.stdout.write(f"  ... and {len(teachers) - 20} more teachers")

        # --- Students ---
        students = by_role.get("STD", [])
        if students:
            self.stdout.write(self.style.NOTICE(f"\n--- STUDENTS ({len(students)} total) ---"))
            self.stdout.write(f'{"Email":<45} {"Name":<25} {"Password"}')
            self.stdout.write("-" * 90)
            for u in students[:20]:
                self.stdout.write(f"{u.email:<45} {u.get_full_name():<25} {_get_pw('STD')}")
            if len(students) > 20:
                self.stdout.write(f"  ... and {len(students) - 20} more students")

        # --- Summary ---
        self.stdout.write(self.style.SUCCESS("\n" + "=" * 110))
        self.stdout.write(self.style.SUCCESS("SUMMARY"))
        self.stdout.write(self.style.SUCCESS("=" * 110))
        self.stdout.write(f"  Total users: {users.count()}")
        for role in sorted(by_role.keys()):
            self.stdout.write(f"    {role:<12}: {len(by_role[role])}")

        # --- Password Reference ---
        self.stdout.write(self.style.SUCCESS("\n" + "=" * 110))
        self.stdout.write(self.style.SUCCESS("PASSWORD REFERENCE (from env vars / defaults)"))
        self.stdout.write(self.style.SUCCESS("=" * 110))
        for env_key, default in DEFAULT_PASSWORDS.items():
            val = os.environ.get(env_key, default)
            self.stdout.write(f"  {env_key:<28} {val}")
