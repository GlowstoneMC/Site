# coding=utf-8

from sqlalchemy import Column, String, Integer, Boolean

from ultros_site.database.common import DeclarativeBase

__author__ = "Momo"


class ProductBranch(DeclarativeBase):
    __tablename__ = "product_branch"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer)
    name = Column(String)
    disabled = Column(Boolean, default=False)
