from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_management.settings')

app = Celery('farm_management')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Celery Beat schedule configuration
app.conf.beat_schedule = {
    # 📧 Weekly Newsletter - Every Monday at 10:00 AM
    'send-weekly-html-newsletter-every-monday-10am': {
        'task': 'Subscriber.tasks.send_weekly_html_newsletter_task',
        'schedule': crontab(minute=0, hour=10, day_of_week='1'),  # Monday at 10:00 AM
    },

    # 🥛 Daily Milk Report - Every day at 10:00 PM
    'send-daily-milk-report-10pm': {
        'task': 'animals.tasks.send_milk_report_daily_task',
        'schedule': crontab(minute=0, hour=22),  # 22:00 (10:00 PM daily)
    },

    # 🐄 Animal Alerts Email - Every day at 9:00 PM
    'send-daily-animal-alerts-9pm': {
        'task': 'animals.tasks.send_animal_alerts_task',
        'schedule': crontab(minute=0, hour=21),  # 21:00 (9:00 PM daily)
    },

    # 🧾 Google Sheets Milk Sync - Every day at 6:00 AM
    'sync-google-sheets-6am': {
        'task': 'animals.tasks.sync_google_sheets',   # 👈 our new task
        'schedule': crontab(minute=0, hour=6),      # runs daily at 6 AM
    },
}

