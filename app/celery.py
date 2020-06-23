import os
import celery

app = celery.Celery('rosascheduler')
#
app.config_from_object()
app.autodiscover_tasks()
