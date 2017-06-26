# coding=utf-8
from celery.signals import task_prerun, task_postrun
from sqlalchemy.orm.exc import NoResultFound

from ultros_site.database.schema.celery_task import CeleryTask
from ultros_site.database_manager import DatabaseManager

__author__ = "Gareth Coles"


db_manager = DatabaseManager()
db_manager.create_engine()
db_manager.load_schema()


def db_add(task_id, name, args, state):
    with db_manager.session() as session:
        row = CeleryTask(task_id=task_id, name=name, args=args, status=state)
        session.add(row)


def db_update_status(task_id, status):
    with db_manager.session() as session:
        try:
            row = session.query(CeleryTask).filter_by(task_id=task_id).one()
        except NoResultFound:
            pass
        else:
            row.status = status


@task_prerun.connect
def task_prerun(signal=None, sender=None, task_id=None, task=None, args=None, kwargs=None, **kw):
    task_args = {
        "args": args,
        "kwargs": kwargs
    }

    db_add(task_id, task.name, task_args, "PENDING")


@task_postrun.connect
def task_postrun(signal=None, sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None, **kw):
    db_update_status(task_id, state)