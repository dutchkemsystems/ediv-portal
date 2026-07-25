"""
Management command to list all principals and vice-principals
with their current details.

Usage:
    python manage.py list_principals_vps
    python manage.py list_principals_vps --csv
"""
import csv
import sys
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'List all principals and vice-principals with their details'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv',
            action='store_true',
            help='Output as CSV format',
        )

    def handle(self, *args, **options):
        output_csv = options['csv']

        # Get all principals and VPs with school info
        principals_vps = User.objects.filter(
            role__in=['PRI', 'VP']
        ).select_related('school_set').order_by('role', 'email')

        if output_csv:
            # CSV output
            writer = csv.writer(sys.stdout)
            writer.writerow(['Email', 'Role', 'First Name', 'Last Name', 'Phone', 'Active', 'School Code'])
            
            for user in principals_vps:
                school_code = ''
                if hasattr(user, 'school_set'):
                    school = user.school_set.first()
                    if school:
                        school_code = school.code
                writer.writerow([
                    user.email,
                    user.get_role_display(),
                    user.first_name,
                    user.last_name,
                    user.phone_number,
                    user.is_active,
                    school_code
                ])
        else:
            # Table output
            self.stdout.write(self.style.NOTICE('\n=== Principals and Vice-Principals ===\n'))
            
            self.stdout.write(f'{"Email":<45} {"Role":<20} {"Name":<30} {"Phone":<15} {"Active"}')
            self.stdout.write('-' * 130)

            for user in principals_vps:
                role_display = 'Principal' if user.role == 'PRI' else 'Vice Principal'
                full_name = f'{user.first_name} {user.last_name}'
                active = 'Yes' if user.is_active else 'No'
                
                self.stdout.write(
                    f'{user.email:<45} {role_display:<20} {full_name:<30} {user.phone_number or "N/A":<15} {active}'
                )

            self.stdout.write(self.style.SUCCESS(
                f'\nTotal: {principals_vps.count()} users'
            ))
