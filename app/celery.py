import os
import celery

user = os.environ["BROKER_USER"]
password = os.environ["BROKER_PASSWORD"]
address = os.environ["BROKER_ADDRESS"]
broker_address = f"amqp://{user}:{password}@{address}"

app = celery.Celery('rosascheduler')

app.conf.update(

    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
)
app.config_from_object()
app.autodiscover_tasks()
