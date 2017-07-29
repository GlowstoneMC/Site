# coding=utf-8
from ultros_site.tasks import config

from celery import Celery

__author__ = "Gareth Coles"


app = Celery(
    "ultros_site",
    broker=config.broker,
    backend=config.backend,
    include=config.include
)

app.conf.beat_schedule = config.beat_schedule


if __name__ == "__main__":
    app.start()
