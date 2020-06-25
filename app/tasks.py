import celery
import json
import threading
import time
from rosatasks.quantum_sim_tasks import simulate_code
from models import Task, TaskStatusEnum, User
from extensions import db
from datetime import datetime
from decimal import *


def queue_simulation(task_id, app):
    task = Task.query.filter_by(id=task_id).first()
    if task is None:
        print(f"Cannot queue task of ID {task_id}")
        return None
    print(f"Queing task {task}")

    code = task.code
    shots = task.shots

    routed_task = simulate_code.s(task_id, code, shots)
    result = routed_task.delay()
    TaskThread(result, app).start()


class TaskThread(threading.Thread):
    def __init__(self, async_result, app):
        threading.Thread.__init__(self)
        self.result = async_result
        self.app = app

    def run(self):
        print("started task thread")
        print(self.result)
        while not self.result.ready():
            print(self.result.status, flush=True)
            time.sleep(1)

        print(self.result.result, flush=True)

        task_id, err, res, schema, seconds = self.result.result
        user_id = None
        with self.app.app_context():
            task = Task.query.filter_by(id=task_id).first()
            if task is None:
                return

            if err != None:
                task.status = TaskStatusEnum.ERROR
                task.response = {'error': err}
            else:
                task.status = TaskStatusEnum.DONE
                task.response = res

            task.end_time = datetime.now()
            task.cost = seconds * 0.10  # 10 gr per second
            user_id = task.user_id
            try:
                db.session.add(task)
                db.session.commit()
            except:
                print("Cannot save results into DB")

        with self.app.app_context():
            user = User.query.filter_by(id=user_id).first()
            if user is None:
                return

        user.balance = Decimal(float(user.balance) - float(task.cost))

        with self.app.app_context():
            try:
                db.session.add(user)
                db.session.commit()
            except:
                print("Cannot update wallet")
