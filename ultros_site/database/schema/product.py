# coding=utf-8

from sqlalchemy import Column, String, Integer, Boolean

from ultros_site.database.common import DeclarativeBase

__author__ = "Momo"


class Product(DeclarativeBase):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    order = Column(Integer, default=1)
    hidden = Column(Boolean)

    url_github = Column(String)
    url_circleci = Column(String)

    def __repr__(self):
        return "<{}(name={}>".format(
            self.__class__.__name__,
            self.name
        )
