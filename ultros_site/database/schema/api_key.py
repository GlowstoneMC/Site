# coding=utf-8
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from ultros_site.database.common import DeclarativeBase

__author__ = "Gareth Coles"


class APIKey(DeclarativeBase):
    __tablename__ = "api_key"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="api_keys")

    name = Column(String)
    key = Column(String, unique=True)

    def __repr__(self):
        return "<{}(user={}, name={})>".format(
            self.__class__.__name__,
            self.user.username, self.name
        )
