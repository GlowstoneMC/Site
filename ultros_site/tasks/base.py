# coding=utf-8
import logging
from celery import Task

from ultros_site.database_manager import DatabaseManager
from ultros_site.email_manager import EmailManager

__author__ = "Gareth Coles"


class DatabaseTask(Task):
    def __init__(self):
        logging.basicConfig(
            format="%(asctime)s | %(levelname)-8s | %(name)-10s | %(message)s",
            level=logging.WARNING
        )

        self.database = DatabaseManager()
        self.database.load_schema()
        self.database.create_engine()


class DatabaseEmailTask(Task):
    def __init__(self):
        logging.basicConfig(
            format="%(asctime)s | %(levelname)-8s | %(name)-10s | %(message)s",
            level=logging.WARNING
        )

        logging.getLogger("CSSUTILS").setLevel(logging.CRITICAL)

        self.database = DatabaseManager()
        self.database.load_schema()
        self.database.create_engine()

        self.email = EmailManager()


class EmailTask(Task):
    def __init__(self):
        logging.basicConfig(
            format="%(asctime)s | %(levelname)-8s | %(name)-10s | %(message)s",
            level=logging.WARNING
        )

        logging.getLogger("CSSUTILS").setLevel(logging.CRITICAL)

        self.email = EmailManager()
