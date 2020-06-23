import celery
import json
from rosatasks.quantum_sim_tasks import simulate_code
from models import Task, TaskStatusEnum
from extensions import db

logger = celery.utils.log.get_task_logger(__name__)


@celery.shared_task(ignore_result=True)
def queue_simulation(task_id):
    task = Task.query.filter_by(id=task_id).first()
    if task is None:
        logger.info("Cannot queue task of ID %d", task_id)
        return None
    logger.info("Queing task %s", task)

    code = task.code
    shots = task.shots

    routed_task = simulate_code.signature(
        (id, code, shots),
        immutable=True,
        options={"queue": "qiskit_queue"}
    )
    celery.chain(routed_task, write_result.s(task_id))()
    logger.info("Task %s queued", task)


@celery.shared_task(ignore_result=True)
def write_result(result, task_id):
    task = Task.query.filter_by(id=task_id).first()
    logger.info("Writing result for task %s", task)
    if task is None:
        return

    id, err, res, schema = result

    if err != None:
        task.status = TaskStatusEnum.error
        task.response = json.JSONEncoder.encode({'error': err})
    else:
        task.status = TaskStatusEnum.done
        task.response = json.JSONEncoder.encode(res)

    try:
        db.session.add(task)
        db.session.commit()
    except:
        logger.error("Cannot save results into DB")
