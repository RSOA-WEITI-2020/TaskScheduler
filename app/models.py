from extensions import db
from sqlalchemy.dialects.mysql import DECIMAL
import enum


class TaskStatusEnum(enum.Enum):
    PENDING = 1
    IN_PROGRESS = 2
    DONE = 3
    ERROR = 4


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    celery_task_id = db.Column(db.Integer, nullable=True)
    user_id = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.DateTime(), nullable=True)
    end_time = db.Column(db.DateTime(), nullable=True)
    code = db.Column(db.Text(), nullable=False)
    shots = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(TaskStatusEnum), nullable=False)
    response = db.Column(db.JSON(), nullable=True)
    cost = db.Column(DECIMAL(precision=6, scale=2,
                             unsigned=True), nullable=True)


class User(db.Model):
    __bind_key__ = 'users'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    balance = db.Column(DECIMAL(precision=10, scale=2,
                                unsigned=True), nullable=False)
    first_name = db.Column(db.String(45), nullable=False)
    last_name = db.Column(db.String(45), nullable=False)
    address = db.Column(db.String(80), nullable=False)
