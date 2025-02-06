from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_management.settings')

app = Celery('farm_management')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Celery Beat schedule configuration (for weekly newsletters)
from celery.schedules import crontab

app.conf.beat_schedule = {
    'send-weekly-html-newsletter-every-monday-10am': {
        'task': 'Subscriber.tasks.send_weekly_html_newsletter_task',
        'schedule': crontab(minute=0, hour=10, day_of_week='1'),  # Every Monday at 10:00 AM
    },
}

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

