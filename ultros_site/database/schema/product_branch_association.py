# coding=utf-8

from sqlalchemy import Column, Integer, ForeignKey

from ultros_site.database.common import DeclarativeBase

__author__ = "Momo"


class ProductBranchAssociation(DeclarativeBase):
    __tablename__ = "product_branch_association"

    id = Column(Integer, primary_key=True)

    product_id = Column(Integer, ForeignKey("product.id"))
    branch_id = Column(Integer, ForeignKey("product_branch.id"))
