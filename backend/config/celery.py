import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.set_default()

# Periodic task schedule for enterprise automation
app.conf.beat_schedule = {
    # Check and auto-escalate overdue files every 30 minutes
    "check-overdue-files": {
        "task": "apps.files.tasks.check_and_escalate_overdue_files",
        "schedule": crontab(minute="*/30"),
    },
    # Process offline sync queue every 15 minutes
    "process-offline-queue": {
        "task": "apps.files.tasks.process_offline_queue",
        "schedule": crontab(minute="*/15"),
    },
    # Send deadline approaching reminders every hour
    "deadline-reminders": {
        "task": "apps.files.tasks.send_deadline_reminders",
        "schedule": crontab(minute=0),  # Every hour at :00
    },
    # Check overdue mails every 30 minutes
    "check-overdue-mails": {
        "task": "apps.communication.tasks.check_overdue_mails",
        "schedule": crontab(minute="*/30"),
    },
    # Send weekly digest every Monday at 8am
    "weekly-digest": {
        "task": "apps.communication.tasks.send_weekly_digest",
        "schedule": crontab(hour=8, minute=0, day_of_week="monday"),
    },
    # Reindex Elasticsearch every 6 hours
    "reindex-search": {
        "task": "apps.files.tasks.reindex_elasticsearch",
        "schedule": crontab(hour="*/6", minute=30),
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
