# coding=utf-8
from ultros_site.tasks.__main__ import app
from ultros_site.tasks.base import EmailTask

__author__ = "Gareth Coles"


@app.task(base=EmailTask, name="send_email")
def send_email(template, recipient, subject, *args, **kwargs):
    send_email.email.send_email(template, recipient, subject, *args, **kwargs)
    return True
