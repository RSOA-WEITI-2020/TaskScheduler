import celery
import json
from rosatasks.quantum_sim_tasks import simulate_code
from models import Task, TaskStatusEnum
from extensions import db

logger = celery.utils.log.get_task_logger(__name__)


def queue_simulation(task_id):
    print("xD")
    task = Task.query.filter_by(id=task_id).first()
    if task is None:
        print(f"Cannot queue task of ID {task_id}")
        return None
    print(f"Queing task {task}")

    code = task.code
    shots = task.shots

    routed_task = simulate_code.s(task_id, code, shots)
    result = routed_task.delay()
    print("started task")
    result.wait()
    print(result.result)

    task = Task.query.filter_by(id=task_id).first()
    if task is None:
        return
    logger.info("asd")
    logger.info(result)
    task_id, err, res, schema = result.result
    if err != None:
        task.status = TaskStatusEnum.error
        task.response = json.dumps({'error': err})
    else:
        task.status = TaskStatusEnum.done
        task.response = json.dumps(result)

    try:
        db.session.add(task)
        db.session.commit()
    except:
        logger.error("Cannot save results into DB")

    return routed_task.id
