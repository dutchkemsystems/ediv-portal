"""
Management command to display all role privileges in a readable format.

Usage:
    python manage.py show_role_privileges
    python manage.py show_role_privileges --role SYSADMIN
    python manage.py show_role_privileges --module finance
"""
import csv
import sys
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.users.models import Privilege, RolePrivilege, Module

User = get_user_model()


class Command(BaseCommand):
    help = 'Display all role privileges'

    def add_arguments(self, parser):
        parser.add_argument(
            '--role',
            type=str,
            help='Filter by specific role (e.g., SYSADMIN, PRI, TCH)',
        )
        parser.add_argument(
            '--module',
            type=str,
            help='Filter by specific module (e.g., finance, students)',
        )
        parser.add_argument(
            '--csv',
            action='store_true',
            help='Output as CSV format',
        )

    def handle(self, *args, **options):
        role_filter = options.get('role')
        module_filter = options.get('module')
        output_csv = options.get('csv')

        # Build query
        queryset = Privilege.objects.all()
        if role_filter:
            queryset = queryset.filter(role=role_filter.upper())
        if module_filter:
            queryset = queryset.filter(module=module_filter.lower())

        queryset = queryset.order_by('role', 'module')

        if output_csv:
            # CSV output
            writer = csv.writer(sys.stdout)
            writer.writerow(['Role', 'Module', 'View', 'Create', 'Edit', 'Delete', 'Approve', 'Export'])
            
            for priv in queryset:
                writer.writerow([
                    priv.role,
                    priv.module,
                    priv.can_view,
                    priv.can_create,
                    priv.can_edit,
                    priv.can_delete,
                    priv.can_approve,
                    priv.can_export,
                ])
        else:
            # Group by role
            roles = {}
            for priv in queryset:
                if priv.role not in roles:
                    roles[priv.role] = []
                roles[priv.role].append(priv)

            self.stdout.write(self.style.NOTICE('\n=== Role Privileges ===\n'))

            for role, privileges in sorted(roles.items()):
                # Get role description
                try:
                    role_priv = RolePrivilege.objects.get(role=role)
                    description = role_priv.description
                except RolePrivilege.DoesNotExist:
                    description = 'No description'

                self.stdout.write(self.style.SUCCESS(f'\n{role}'))
                self.stdout.write(f'  Description: {description}')
                self.stdout.write(f'  {"Module":<20} {"View":<8} {"Create":<8} {"Edit":<8} {"Delete":<8} {"Approve":<8} {"Export":<8}')
                self.stdout.write(f'  {"-" * 70}')

                for priv in privileges:
                    self.stdout.write(
                        f'  {priv.module:<20} '
                        f'{"✓" if priv.can_view else "✗":<8} '
                        f'{"✓" if priv.can_create else "✗":<8} '
                        f'{"✓" if priv.can_edit else "✗":<8} '
                        f'{"✓" if priv.can_delete else "✗":<8} '
                        f'{"✓" if priv.can_approve else "✗":<8} '
                        f'{"✓" if priv.can_export else "✗":<8}'
                    )

            # Summary
            total_privileges = queryset.count()
            total_roles = len(roles)
            self.stdout.write(self.style.SUCCESS(f'\n{"=" * 50}'))
            self.stdout.write(self.style.SUCCESS(f'Total: {total_privileges} privileges across {total_roles} roles'))
