import json
from typing import (
    MutableMapping,
    Type,
)
from flask_restful import (
    Resource,
    reqparse,
    abort,
)
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity,
    get_raw_jwt
)
from extensions import (
    jwt,
    db
)

from models import (
    Task,
    TaskStatusEnum
)

from tasks import queue_simulation
from celery.result import AsyncResult
from datetime import datetime
from flask import jsonify


class BaseResource(Resource):
    __resources: MutableMapping[str, Type[Resource]] = {}

    def __init_subclass__(cls, *args, **kwargs):
        cls.__resources[cls.path] = cls
        super().__init_subclass__(*args, **kwargs)

    @classmethod
    def register(cls, api):
        for path, res in cls.__resources.items():
            api.add_resource(res, path)


class Tasks(BaseResource):
    path = "/v1/task"

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument(
            'code', help='This field cannot be blank', required=True)
        self.parser.add_argument(
            'shots', help='This field cannot be blank', required=True)

    @jwt_required
    def post(self):
        data = self.parser.parse_args()
        user_id = get_jwt_identity()
        code = data['code']
        shots = data['shots']

        task = Task(
            user_id=user_id,
            code=code,
            shots=shots,
            status=TaskStatusEnum.PENDING,
            start_time=datetime.now()
        )

        try:
            db.session.add(task)
            db.session.commit()
        except:
            abort(500)

        celery_task_id = queue_simulation(task.id, db.get_app())
        task.celery_task_id = celery_task_id

        try:
            db.session.add(task)
            db.session.commit()
        except:
            abort(500)

        return {'message': 'ok', 'task_id': task.id}

    @jwt_required
    def get(self):
        user_id = get_jwt_identity()

        tasks = Task.query.filter_by(user_id=user_id).all()
        res = []
        for task in tasks:
            start_str = None
            end_str = None
            cost = None
            try:
                start_str = task.start_time.strftime("%Y-%m-%dT%H:%M:%S")
            except:
                pass
            try:
                end_str = task.end_time.strftime("%Y-%m-%dT%H:%M:%S")
            except:
                pass
            try:
                cost = float(task.cost)
            except:
                pass

            res.append({'id': task.id,
                        'user_id': task.user_id,
                        'start_time': start_str,
                        'end_time': end_str,
                        'code': task.code,
                        'shots': task.shots,
                        'status': task.status.name,
                        'response': task.response,
                        'cost': cost
                        })

        return res


class SingleTask(BaseResource):
    path = "/v1/task/<int:task_id>"

    def __init__(self):
        pass

    @jwt_required
    def get(self, task_id):
        user_id = get_jwt_identity()

        task = Task.query.filter_by(id=task_id, user_id=user_id).first()
        if task is None:
            return

        start_str = None
        end_str = None
        cost = None
        try:
            start_str = task.start_time.strftime("%d-%m-%YT%H:%M:%S")
        except:
            pass
        try:
            end_str = task.end_time.strftime("%d-%m-%YT%H:%M:%S")
        except:
            pass
        try:
            cost = float(task.cost)
        except:
            pass

        return {'id': task.id,
                'user_id': task.user_id,
                'start_time': start_str,
                'end_time': end_str,
                'code': task.code,
                'shots': task.shots,
                'status': task.status.name,
                'response': task.response,
                'cost': cost
                }
