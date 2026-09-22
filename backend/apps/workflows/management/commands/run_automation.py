"""
Management command to run the agentic automation engine.
"""

from django.core.management.base import BaseCommand

from apps.workflows.automation import AutomationEngine, run_automation


class Command(BaseCommand):
    help = "Run the agentic automation engine for file/mail distribution"

    def add_arguments(self, parser):
        parser.add_argument(
            "--action",
            type=str,
            default="full",
            choices=["full", "process", "overdue", "rebalance", "summary"],
            help="Action to run: full (all), process (pending items), overdue (check overdue), "
            "rebalance (workload), summary (daily summaries)",
        )

    def handle(self, *args, **options):
        action = options["action"]
        engine = AutomationEngine()

        self.stdout.write(self.style.SUCCESS(f"Running automation: {action}"))

        if action == "full":
            results = engine.run_full_cycle()
        elif action == "process":
            results = engine.process_all_pending_items()
        elif action == "overdue":
            results = engine.check_all_overdue_items()
        elif action == "rebalance":
            results = engine.rebalance_all_workloads()
        elif action == "summary":
            results = engine.generate_all_daily_summaries()
        else:
            results = {}

        self.stdout.write(self.style.SUCCESS(f"Automation complete: {results}"))
