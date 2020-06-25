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
    db,
    AlchemyEncoder
)

from models import (
    Task,
    TaskStatusEnum
)

from tasks import queue_simulation
from celery.result import AsyncResult


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

    # @jwt_required
    def post(self):
        data = self.parser.parse_args()
        user_id = get_jwt_identity()
        user_id = 0
        code = data['code']
        shots = data['shots']

        task = Task(
            user_id=user_id,
            code=code,
            shots=shots,
            status=TaskStatusEnum.pending
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

        return {'message': 'ok', 'celery_task_id': celery_task_id}


class SingleTask(BaseResource):
    path = "/v1/task/<int:id>"

    def __init__(self):
        pass

#   @jwt_required
    def get(self, id):
        task = Task.query.filter_by(id=id).first()
        if task is None:
            return

        return json.loads(json.dumps(task, cls=AlchemyEncoder))


class TaskStatus(BaseResource):
    path = "/v1/task/<int:id>/status"

    def __init__(self):
        pass

#    @jwt_required
    def get(self, id):
        task = Task.query.filter_by(id=id).first()
        if task is None:
            abort(500)

        celery_task_id = task.celery_task_id

        task = AsyncResult(celery_task_id)
        data = {
            'state': task.state,
            'result': task.result,
        }
        return json.dumps(data)
