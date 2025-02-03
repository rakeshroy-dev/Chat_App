from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Configure Celery using Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Discover tasks in Django apps
app.autodiscover_tasks()