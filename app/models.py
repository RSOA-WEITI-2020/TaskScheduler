from extensions import db
from sqlalchemy.dialects.mysql import DECIMAL
import enum


class TaskStatusEnum(enum.Enum):
    pending = "PENDING"
    in_progress = "IN PROGRESS"
    done = "DONE"
    error = "ERROR"


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
