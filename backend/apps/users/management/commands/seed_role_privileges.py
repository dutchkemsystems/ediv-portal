"""
Management command to seed all role privileges for the Education District IV Portal.

Creates RolePrivilege templates and granular Privilege entries for all 22 roles
based on the dashboard access patterns defined in the frontend.

Usage:
    python manage.py seed_role_privileges --dry-run
    python manage.py seed_role_privileges
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.users.models import Privilege, RolePrivilege, Module

User = get_user_model()


# ---------------------------------------------------------------------------
# Role definitions with descriptions
# ---------------------------------------------------------------------------
ROLE_DEFINITIONS = {
    'SYSADMIN': 'System Administrator - Full system access with all permissions',
    'TG_PS': 'Tutor General/Permanent Secretary - Head of Education District with full oversight',
    'HR': 'Admin & HR Head - Human resources and staff management',
    'FIN': 'Finance Director - Financial operations and budgeting',
    'AUDIT': 'Internal Audit Head - Compliance and audit operations',
    'QA': 'Quality Assurance Head - Quality standards and inspection',
    'CC': 'Co-Curricular Head - Co-curricular activities and programs',
    'EMIS': 'EMIS Head - Education management information system',
    'PLAN': 'Planning Head - Strategic planning and analytics',
    'PROC': 'Procurement Head - Procurement and supply chain',
    'PA': 'Public Affairs Head - Communication and public relations',
    'SA': 'Schools Admin Head - School administration oversight',
    'FRENCH': 'French Unit Head - French language programs',
    'REG': 'Registry Head - Document and file management',
    'PRI': 'Principal - School head with full school management',
    'VP': 'Vice Principal - School deputy with student/staff oversight',
    'TCH': 'Teacher - Classroom management and student tracking',
    'STD': 'Student - Student portal access',
    'PAR': 'Parent - Parent portal access',
    'REG_OFF': 'Registry Officer - Document handling operations',
    'SA_OFF': 'School Admin Officer - School administrative support',
}


# ---------------------------------------------------------------------------
# Module access matrix: role -> list of modules with CRUD permissions
# Format: (module, can_view, can_create, can_edit, can_delete, can_approve, can_export)
# ---------------------------------------------------------------------------
MODULE_ACCESS = {
    # ==================== ADMIN LEVEL (Full Access) ====================
    'SYSADMIN': [
        ('dashboard', True, True, True, True, True, True),
        ('schools', True, True, True, True, True, True),
        ('staff', True, True, True, True, True, True),
        ('students', True, True, True, True, True, True),
        ('attendance', True, True, True, True, True, True),
        ('academics', True, True, True, True, True, True),
        ('finance', True, True, True, True, True, True),
        ('grants', True, True, True, True, True, True),
        ('hr', True, True, True, True, True, True),
        ('registry', True, True, True, True, True, True),
        ('files', True, True, True, True, True, True),
        ('workflows', True, True, True, True, True, True),
        ('communication', True, True, True, True, True, True),
        ('notifications', True, True, True, True, True, True),
        ('timetable', True, True, True, True, True, True),
        ('transport', True, True, True, True, True, True),
        ('assets', True, True, True, True, True, True),
        ('discipline', True, True, True, True, True, True),
        ('library', True, True, True, True, True, True),
        ('e_learning', True, True, True, True, True, True),
        ('wellness', True, True, True, True, True, True),
        ('alumni', True, True, True, True, True, True),
        ('infrastructure', True, True, True, True, True, True),
        ('inspection', True, True, True, True, True, True),
        ('french', True, True, True, True, True, True),
        ('co_curricular', True, True, True, True, True, True),
        ('cpd', True, True, True, True, True, True),
        ('reports', True, True, True, True, True, True),
        ('analytics', True, True, True, True, True, True),
        ('privileges', True, True, True, True, True, True),
    ],

    'TG_PS': [
        ('dashboard', True, True, True, True, True, True),
        ('schools', True, True, True, True, True, True),
        ('staff', True, True, True, True, True, True),
        ('students', True, True, True, True, True, True),
        ('attendance', True, True, True, True, True, True),
        ('academics', True, True, True, True, True, True),
        ('finance', True, True, True, True, True, True),
        ('grants', True, True, True, True, True, True),
        ('hr', True, True, True, True, True, True),
        ('registry', True, True, True, True, True, True),
        ('files', True, True, True, True, True, True),
        ('workflows', True, True, True, True, True, True),
        ('communication', True, True, True, True, True, True),
        ('notifications', True, True, True, True, True, True),
        ('timetable', True, True, True, True, True, True),
        ('transport', True, True, True, True, True, True),
        ('assets', True, True, True, True, True, True),
        ('discipline', True, True, True, True, True, True),
        ('library', True, True, True, True, True, True),
        ('e_learning', True, True, True, True, True, True),
        ('wellness', True, True, True, True, True, True),
        ('alumni', True, True, True, True, True, True),
        ('infrastructure', True, True, True, True, True, True),
        ('inspection', True, True, True, True, True, True),
        ('french', True, True, True, True, True, True),
        ('co_curricular', True, True, True, True, True, True),
        ('cpd', True, True, True, True, True, True),
        ('reports', True, True, True, True, True, True),
        ('analytics', True, True, True, True, True, True),
        ('privileges', True, True, True, True, True, True),
    ],

    # ==================== DEPARTMENT HEADS ====================
    'HR': [
        ('dashboard', True, False, False, False, False, True),
        ('staff', True, True, True, False, False, True),
        ('hr', True, True, True, False, True, True),
        ('grants', True, True, True, False, False, True),
        ('reports', True, True, True, False, False, True),
        ('notifications', True, True, False, False, False, False),
    ],

    'FIN': [
        ('dashboard', True, False, False, False, False, True),
        ('finance', True, True, True, False, True, True),
        ('grants', True, True, True, False, True, True),
        ('reports', True, True, True, False, False, True),
        ('notifications', True, True, False, False, False, False),
    ],

    'AUDIT': [
        ('dashboard', True, False, False, False, False, True),
        ('audit', True, True, True, False, True, True),
        ('reports', True, True, True, False, False, True),
        ('notifications', True, True, False, False, False, False),
    ],

    'QA': [
        ('dashboard', True, False, False, False, False, True),
        ('inspection', True, True, True, False, True, True),
        ('reports', True, True, True, False, False, True),
        ('notifications', True, True, False, False, False, False),
    ],

    'CC': [
        ('dashboard', True, False, False, False, False, True),
        ('co_curricular', True, True, True, False, True, True),
        ('french', True, True, True, False, False, True),
        ('reports', True, True, True, False, False, True),
        ('notifications', True, True, False, False, False, False),
    ],

    'EMIS': [
        ('dashboard', True, False, False, False, False, True),
        ('analytics', True, True, True, False, False, True),
        ('reports', True, True, True, False, False, True),
        ('notifications', True, True, False, False, False, False),
    ],

    'PLAN': [
        ('dashboard', True, False, False, False, False, True),
        ('analytics', True, True, True, False, False, True),
        ('reports', True, True, True, False, False, True),
        ('notifications', True, True, False, False, False, False),
    ],

    'PROC': [
        ('dashboard', True, False, False, False, False, True),
        ('assets', True, True, True, False, True, True),
        ('reports', True, True, True, False, False, True),
        ('notifications', True, True, False, False, False, False),
    ],

    'PA': [
        ('dashboard', True, False, False, False, False, True),
        ('communication', True, True, True, False, True, True),
        ('reports', True, True, True, False, False, True),
        ('notifications', True, True, False, False, False, False),
    ],

    'SA': [
        ('dashboard', True, False, False, False, False, True),
        ('schools', True, True, True, False, False, True),
        ('students', True, True, True, False, False, True),
        ('reports', True, True, True, False, False, True),
        ('notifications', True, True, False, False, False, False),
    ],

    'FRENCH': [
        ('dashboard', True, False, False, False, False, True),
        ('french', True, True, True, False, True, True),
        ('co_curricular', True, True, True, False, False, True),
        ('reports', True, True, True, False, False, True),
        ('notifications', True, True, False, False, False, False),
    ],

    'REG': [
        ('dashboard', True, False, False, False, False, True),
        ('registry', True, True, True, True, True, True),
        ('files', True, True, True, True, True, True),
        ('workflows', True, True, True, True, True, True),
        ('notifications', True, True, False, False, False, False),
    ],

    # ==================== SCHOOL STAFF ====================
    'PRI': [
        ('dashboard', True, False, False, False, False, True),
        ('schools', True, True, True, False, False, True),
        ('students', True, True, True, False, False, True),
        ('staff', True, True, True, False, False, True),
        ('academics', True, True, True, False, True, True),
        ('attendance', True, True, True, False, False, True),
        ('timetable', True, True, True, False, False, True),
        ('reports', True, True, True, False, False, True),
        ('discipline', True, True, True, False, True, True),
        ('library', True, True, True, False, False, True),
        ('notifications', True, True, False, False, False, False),
    ],

    'VP': [
        ('dashboard', True, False, False, False, False, True),
        ('students', True, True, True, False, False, True),
        ('staff', True, True, True, False, False, True),
        ('academics', True, True, True, False, False, True),
        ('attendance', True, True, True, False, False, True),
        ('timetable', True, True, True, False, False, True),
        ('reports', True, True, True, False, False, True),
        ('discipline', True, True, True, False, True, True),
        ('notifications', True, True, False, False, False, False),
    ],

    'TCH': [
        ('dashboard', True, False, False, False, False, True),
        ('students', True, False, True, False, False, True),
        ('academics', True, True, True, False, False, True),
        ('attendance', True, True, True, False, False, True),
        ('timetable', True, False, False, False, False, True),
        ('e_learning', True, True, True, False, False, True),
        ('discipline', True, True, False, False, False, True),
        ('notifications', True, True, False, False, False, False),
    ],

    # ==================== SUPPORT STAFF ====================
    'REG_OFF': [
        ('dashboard', True, False, False, False, False, True),
        ('registry', True, True, True, False, False, True),
        ('files', True, True, True, False, False, True),
        ('workflows', True, True, True, False, False, True),
        ('notifications', True, True, False, False, False, False),
    ],

    'SA_OFF': [
        ('dashboard', True, False, False, False, False, True),
        ('schools', True, True, True, False, False, True),
        ('students', True, True, True, False, False, True),
        ('reports', True, True, True, False, False, True),
        ('notifications', True, True, False, False, False, False),
    ],

    # ==================== END USERS ====================
    'STD': [
        ('dashboard', True, False, False, False, False, True),
        ('academics', True, False, False, False, False, True),
        ('attendance', True, False, False, False, False, True),
        ('library', True, True, False, False, False, True),
        ('e_learning', True, False, False, False, False, True),
        ('notifications', True, True, False, False, False, False),
    ],

    'PAR': [
        ('dashboard', True, False, False, False, False, True),
        ('students', True, False, False, False, False, True),
        ('finance', True, False, False, False, False, True),
        ('communication', True, True, False, False, False, False),
        ('notifications', True, True, False, False, False, False),
    ],
}


class Command(BaseCommand):
    help = 'Seed all role privileges for the Education District IV Portal'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without making them',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete all existing privileges before seeding',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        reset = options['reset']

        self.stdout.write(self.style.NOTICE('\n=== Seeding Role Privileges ===\n'))

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made\n'))

        # Reset if requested
        if reset and not dry_run:
            self.stdout.write(self.style.WARNING('Deleting existing privileges...'))
            Privilege.objects.all().delete()
            RolePrivilege.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Deleted all existing privileges\n'))

        # Create RolePrivilege templates
        self.stdout.write(self.style.NOTICE('Creating RolePrivilege templates...'))
        templates_created = 0
        for role, description in ROLE_DEFINITIONS.items():
            if dry_run:
                exists = RolePrivilege.objects.filter(role=role).exists()
                if not exists:
                    self.stdout.write(f'  Would create: {role} - {description[:50]}...')
                    templates_created += 1
            else:
                obj, created = RolePrivilege.objects.get_or_create(
                    role=role,
                    defaults={'description': description}
                )
                if created:
                    templates_created += 1
                    self.stdout.write(f'  + Created: {role}')
                else:
                    self.stdout.write(f'  - Exists: {role}')

        self.stdout.write(self.style.SUCCESS(f'\nTemplates: {templates_created} created\n'))

        # Create Privilege entries
        self.stdout.write(self.style.NOTICE('Creating Privilege entries...'))
        privileges_created = 0
        privileges_skipped = 0

        for role, modules in MODULE_ACCESS.items():
            self.stdout.write(f'\n  Role: {role}')
            for module_data in modules:
                module = module_data[0]
                can_view = module_data[1]
                can_create = module_data[2]
                can_edit = module_data[3]
                can_delete = module_data[4]
                can_approve = module_data[5]
                can_export = module_data[6]

                perms = []
                if can_view: perms.append('view')
                if can_create: perms.append('create')
                if can_edit: perms.append('edit')
                if can_delete: perms.append('delete')
                if can_approve: perms.append('approve')
                if can_export: perms.append('export')

                if dry_run:
                    exists = Privilege.objects.filter(role=role, module=module).exists()
                    if not exists:
                        self.stdout.write(f'    + {module}: {", ".join(perms)}')
                        privileges_created += 1
                    else:
                        privileges_skipped += 1
                else:
                    obj, created = Privilege.objects.get_or_create(
                        role=role,
                        module=module,
                        defaults={
                            'can_view': can_view,
                            'can_create': can_create,
                            'can_edit': can_edit,
                            'can_delete': can_delete,
                            'can_approve': can_approve,
                            'can_export': can_export,
                        }
                    )
                    if created:
                        privileges_created += 1
                        self.stdout.write(f'    + {module}: {", ".join(perms)}')
                    else:
                        privileges_skipped += 1

        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n{"=" * 50}'))
        self.stdout.write(self.style.SUCCESS(f'SUMMARY'))
        self.stdout.write(self.style.SUCCESS(f'{"=" * 50}'))
        self.stdout.write(self.style.SUCCESS(f'Templates: {templates_created} {"would be " if dry_run else ""}created'))
        self.stdout.write(self.style.SUCCESS(f'Privileges: {privileges_created} {"would be " if dry_run else ""}created'))
        if privileges_skipped > 0:
            self.stdout.write(self.style.WARNING(f'Privileges: {privileges_skipped} already exist (skipped)'))

        if dry_run:
            self.stdout.write(self.style.WARNING('\nRun without --dry-run to apply changes'))
