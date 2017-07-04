# coding=utf-8
from celery import Celery

__author__ = "Gareth Coles"


app = Celery(
    "ultros_site",
    broker="amqp://storage:5672/glowstone",
    backend="redis://storage:6379/2",
    include=[
        "ultros_site.tasks.comments",
        "ultros_site.tasks.common",
        "ultros_site.tasks.discord",
        "ultros_site.tasks.email",
        "ultros_site.tasks.github_import",
        "ultros_site.tasks.nodebb"
        "ultros_site.tasks.notify"
        "ultros_site.tasks.twitter"
    ]
)


if __name__ == "__main__":
    app.start()
