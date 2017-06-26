# coding=utf-8
import datetime

from ultros_site.database.schema.celery_task import CeleryTask
from ultros_site.database.schema.user import User
from ultros_site.database.schema.session import Session

from ultros_site.database_manager import DatabaseManager

__author__ = "Gareth Coles"

manager = DatabaseManager()
now = datetime.datetime.now()

print("Running housekeeping tasks")
print("")
print("> Cleaning expired sessions...")

sessions = 0
users = 0

manager.create_engine()
manager.load_schema()
db_session = manager.create_session()

try:
    for session in db_session.query(Session).all():
        if now > session.expires:
            db_session.delete(session)
            sessions += 1
except Exception as e:
    print("  Failed: {}".format(e))
    db_session.rollback()
else:
    print("  {} sessions deleted.".format(sessions))
    db_session.commit()

db_session.close()

print("")
print("> Cleaning old un-verified users...")

db_session = manager.create_session()

try:
    for user in db_session.query(User).all():
        if not user.email_verified:
            if now - user.created > datetime.timedelta(hours=24):
                db_session.delete(user)
                users += 1
except Exception as e:
    print("  Failed: {}".format(e))
    db_session.rollback()
else:
    print("  {} users deleted.".format(users))
    db_session.commit()

db_session.close()

print("")
print("> Cleaning old celery tasks...")

db_session = manager.create_session()
tasks = 0

try:
    for task in db_session.query(CeleryTask).all():
        if now - task.created_date > datetime.timedelta(hours=48):
            db_session.delete(task)
            tasks += 1
except Exception as e:
    print("  Failed: {}".format(e))
    db_session.rollback()
else:
    print("  {} tasks deleted.".format(tasks))
    db_session.commit()

db_session.close()

print("")
print("Housekeeping tasks done.")
