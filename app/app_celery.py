from rosatasks.quantum_sim_tasks import simulate_code
import os
import celery

user = os.environ["BROKER_USER"]
password = os.environ["BROKER_PASSWORD"]
address = os.environ["BROKER_ADDRESS"]
broker_address = f"amqp://{user}:{password}@{address}"

app_celery = celery.Celery(
    'rosascheduler', broker=broker_address, backend=broker_address)

app_celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
)
app_celery.set_default()
app_celery.autodiscover_tasks()

print(app_celery.tasks)
