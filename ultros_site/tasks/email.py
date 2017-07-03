# coding=utf-8
import logging

from celery import Task

from ultros_site.email_manager import EmailManager
from ultros_site.tasks.__main__ import app

__author__ = "Gareth Coles"


class EmailTask(Task):
    def __init__(self):
        logging.basicConfig(
            format="%(asctime)s | %(levelname)-8s | %(name)-10s | %(message)s",
            level=logging.WARNING
        )

        logging.getLogger("CSSUTILS").setLevel(logging.CRITICAL)

        self.email = EmailManager()


@app.task(base=EmailTask, name="send_email")
def send_email(template, recipient, subject, *args, **kwargs):
    send_email.email.send_email(template, recipient, subject, *args, **kwargs)
    return True
