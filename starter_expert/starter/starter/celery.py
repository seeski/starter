import os
from django.conf import settings
from celery.schedules import crontab
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'starter.settings')

app = Celery('starter')
app.conf.enable_utc = False

app.conf.update(timezone='Europe/Moscow')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'update-requests-file': {
    'task': 'wb.tasks.update_requests_task',
    'schedule': crontab(hour=15, minute=12),
}}


#
#
# app.conf.beat_schedule['indexer-daily-report-wb'] = {
#         'task': 'wb.tasks.create_indexer_reports_task',
#         'schedule': crontab(minute=15, hour=18),
#     }
#
# # app.conf.beat_schedule['indexer-daily-report-ozon'] = {
# #         'task': 'ozon.tasks.create_indexer_reports_task',
# #         'schedule': crontab(hour=18, minute=0),
# #     }
#
# app.conf.beat_schedule['scraping-phrases'] = {
#         'task': 'wb.tasks.start_scraping_all_phrases',
#         'schedule': crontab(hour=0, minute=0, day_of_month='8'),
#     }
#
# app.conf.beat_schedule['quick-indexation-daily-cleaning-wb'] =  {
#     'task': 'wb.tasks.clean_quick_indexation_task',
#     'schedule': crontab(hour=14, minute=0),
# }

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


# CELERYD_CONCURRENCY = 12


# CELERYD_CONCURRENCY = 12