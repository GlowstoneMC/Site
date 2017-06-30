# coding=utf-8
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from ultros_site.database.common import DeclarativeBase

__author__ = "Gareth Coles"


class NewsPost(DeclarativeBase):
    __tablename__ = "news_post"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="news_posts")

    posted = Column(DateTime)

    title = Column(String)
    markdown = Column(String)
    html = Column(String)
    summary = Column(String, default=None)
    published = Column(Boolean, default=True)

    def __repr__(self):
        return "<{}(user={}, title={}. posted={})>".format(
            self.__class__.__name__,
            self.user.username, self.title, self.posted
        )
