# coding=utf-8
import datetime

from ultros_site.database.schema.celery_task import CeleryTask
from ultros_site.database.schema.session import Session
from ultros_site.database.schema.user import User
from ultros_site.tasks.__main__ import app
from ultros_site.tasks.base import DatabaseTask

__author__ = "Gareth Coles"


@app.task(base=DatabaseTask, name="scheduled_clean_sessions")
def clean_sessions():
    now = datetime.datetime.now()
    sessions = 0

    with clean_sessions.database.session() as db_session:
        for session in db_session.query(Session).all():
            if now > session.expires:
                db_session.delete(session)
                sessions += 1

    return sessions


@app.task(base=DatabaseTask, name="scheduled_clean_users")
def clean_users():
    now = datetime.datetime.now()
    users = 0

    with clean_users.database.session() as db_session:
        for user in db_session.query(User).all():
            if not user.email_verified:
                if now - user.created > datetime.timedelta(hours=24):
                    db_session.delete(user)
                    users += 1

    return users


@app.task(base=DatabaseTask, name="scheduled_clean_tasks")
def clean_tasks():
    now = datetime.datetime.now()
    tasks = 0

    with clean_tasks.database.session() as db_session:
        for task in db_session.query(CeleryTask).all():
            if now - task.created_date > datetime.timedelta(hours=48):
                db_session.delete(task)
                tasks += 1

    return tasks
