# coding=utf-8
from celery.schedules import crontab

__author__ = "Gareth Coles"


broker = "amqp://guest:guest@glowstone-rabbitmq:5672/glowstone"
backend = "redis://glowstone-site-redis:6379/0"

include = [
    "ultros_site.tasks.builds",
    "ultros_site.tasks.common",
    "ultros_site.tasks.discord",
    "ultros_site.tasks.email",
    "ultros_site.tasks.nodebb",
    "ultros_site.tasks.notify",
    "ultros_site.tasks.scheduled",
    "ultros_site.tasks.twitter"
]

beat_schedule = {
    "clean_sessions": {
        "task": "scheduled_clean_sessions",
        "schedule": crontab(hour=0, minute=0),
        "args": ()
    },

    "clean_users": {
        "task": "scheduled_clean_users",
        "schedule": crontab(hour=1, minute=0),
        "args": ()
    },

    "clean_tasks": {
        "task": "scheduled_clean_tasks",
        "schedule": crontab(hour=2, minute=0),
        "args": ()
    }
}
