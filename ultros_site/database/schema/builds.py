from sqlalchemy import Column, String, Integer, Boolean

from ultros_site.database.common import DeclarativeBase

__author__ = "Momo"


class Product(DeclarativeBase):
    __tablename__ = "product"

    key = Column(Integer, primary_key=True)
    id = Column(String)
    index = Column(Integer)
    hidden = Column(Boolean)
    url_github = Column(String)
    url_circleci = Column(String)

