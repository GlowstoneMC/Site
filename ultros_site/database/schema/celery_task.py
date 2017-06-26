# coding=utf-8
import datetime
from sqlalchemy import Column, Integer, String, JSON, DateTime

from ultros_site.database.common import DeclarativeBase

__author__ = "Gareth Coles"


class CeleryTask(DeclarativeBase):
    __tablename__ = "celery_task"

    id = Column(Integer, primary_key=True)
    task_id = Column(String, unique=True)
    name = Column(String)
    args = Column(JSON)

    created_date = Column(DateTime, default=datetime.datetime.now)
    status = Column(String)

    def __repr__(self):
        return "<{}(key={}, value={})>".format(
            self.__class__.__name__,
            self.key, self.value
        )
