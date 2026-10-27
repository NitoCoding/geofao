"""
Celery Configuration untuk GIS Portal

Setup Celery untuk background tasks (analisis kesesuaian lahan).
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Create Celery app
app = Celery('gisportal')

# Load config from Django settings (namespace='CELERY')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks dari semua installed apps
app.autodiscover_tasks()

app.conf.timezone = 'Asia/Singapore'
app.conf.beat_schedule = {
    'cleanup-temp-midnight': {
        'task': 'apps.spatial.tasks.cleanup_old_temp_files',
        'schedule': crontab(hour=0, minute=0),
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task untuk testing Celery setup"""
    print(f'Request: {self.request!r}')
