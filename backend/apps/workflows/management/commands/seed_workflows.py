from django.core.management.base import BaseCommand

from apps.workflows.services.workflow_service import WorkflowService


class Command(BaseCommand):
    help = "Seed all configured workflow definitions into Workflow/WorkflowStep models"

    def add_arguments(self, parser):
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Update descriptions and roles of existing workflow steps",
        )

    def handle(self, *args, **options):
        stats = WorkflowService.seed_all(overwrite=options["overwrite"])
        self.stdout.write(
            self.style.SUCCESS(f'Workflows seeded: {stats["created"]} created, {stats["updated"]} updated')
        )
