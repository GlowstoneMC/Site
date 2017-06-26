# coding=utf-8
from celery import Celery
from celery.signals import task_prerun, task_postrun

from ultros_site.tasks.common import db_add, db_update_status

__author__ = "Gareth Coles"


app = Celery(
    "ultros_site",
    broker="amqp://storage:5672/glowstone",
    backend="redis://storage:6379/2",
    include=[
        "ultros_site.tasks.email",
        "ultros_site.tasks.github_import",
        "ultros_site.tasks.notify"
    ]
)


@task_prerun.connect()
def task_prerun(signal=None, sender=None, task_id=None, task=None, args=None, kwargs=None):
    task_args = {
        "args": args,
        "kwargs": kwargs
    }

    db_add(task_id, task.name, task_args, "PENDING")


@task_postrun.connect()
def task_postrun(signal=None, sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None):
    db_update_status(task_id, state)


if __name__ == "__main__":
    app.start()
