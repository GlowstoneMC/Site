# coding=utf-8
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship

from ultros_site.database.common import DeclarativeBase

__author__ = "Gareth Coles"


class User(DeclarativeBase):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    created = Column(DateTime)
    admin = Column(Boolean)

    email = Column(String, unique=True)
    email_verified = Column(Boolean, default=False)

    mfa_token = Column(String(length=16), nullable=True)

    sessions = relationship("Session", back_populates="user", cascade="all, delete, delete-orphan")
    email_code = relationship("EmailCode", back_populates="user", uselist=False, cascade="all, delete, delete-orphan")

    def __repr__(self):
        return "<{}(id={}, username={}, email={}, verified={}, sessions={})>".format(
            self.__class__.__name__,
            self.id, self.username, self.email, self.email_verified, len(self.sessions)
        )
