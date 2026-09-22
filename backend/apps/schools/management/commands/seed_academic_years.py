from datetime import date

from django.core.management.base import BaseCommand

from apps.schools.models import School, SchoolAcademicYear


class Command(BaseCommand):
    help = "Seed current academic year (2025/2026) for all schools"

    def add_arguments(self, parser):
        parser.add_argument(
            "--year",
            type=str,
            default="2025/2026",
            help="Academic year to seed (default: 2025/2026)",
        )
        parser.add_argument(
            "--start-date",
            type=str,
            default="2025-09-15",
            help="Term start date YYYY-MM-DD (default: 2025-09-15)",
        )
        parser.add_argument(
            "--end-date",
            type=str,
            default="2026-07-11",
            help="Term end date YYYY-MM-DD (default: 2026-07-11)",
        )

    def handle(self, *args, **options):
        year = options["year"]
        start_date = date.fromisoformat(options["start_date"])
        end_date = date.fromisoformat(options["end_date"])

        schools = School.objects.all()
        if not schools.exists():
            self.stdout.write(self.style.WARNING("No schools found. Run seed_schools first."))
            return

        self.stdout.write(self.style.NOTICE(f"Seeding academic year {year} for {schools.count()} schools..."))

        created_count = 0
        skipped_count = 0

        for school in schools:
            _, created = SchoolAcademicYear.objects.get_or_create(
                school=school,
                year=year,
                defaults={
                    "start_date": start_date,
                    "end_date": end_date,
                    "is_current": True,
                },
            )
            if created:
                created_count += 1
                self.stdout.write(f"  + [{school.code}] {school.name} - {year}")
            else:
                skipped_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"\nDone! {created_count} academic years created, {skipped_count} already existed.")
        )
