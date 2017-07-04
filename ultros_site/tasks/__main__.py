# coding=utf-8
from celery import Celery
from celery.schedules import crontab

__author__ = "Gareth Coles"


app = Celery(
    "ultros_site",
    broker="amqp://storage:5672/glowstone",
    backend="redis://storage:6379/2",
    include=[
        "ultros_site.tasks.common",
        "ultros_site.tasks.discord",
        "ultros_site.tasks.email",
        "ultros_site.tasks.github_import",
        "ultros_site.tasks.nodebb"
        "ultros_site.tasks.notify"
        "ultros_site.tasks.scheduled"
        "ultros_site.tasks.twitter"
    ]
)

app.conf.beat_schedule = {
    "clean_sessions": {
        "task": "scheduled_clean_sessions",
        "schedule": crontab(hour=0),
        "args": ()
    },

    "clean_users": {
        "task": "scheduled_clean_users",
        "schedule": crontab(hour=1),
        "args": ()
    },

    "clean_tasks": {
        "task": "scheduled_clean_tasks",
        "schedule": crontab(hour=2),
        "args": ()
    }
}


if __name__ == "__main__":
    app.start()
