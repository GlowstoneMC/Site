# coding=utf-8

from sqlalchemy import Column, String, Integer, Boolean, UniqueConstraint, ForeignKey

from ultros_site.database.common import DeclarativeBase

__author__ = "Momo"


class ProductBranch(DeclarativeBase):
    __tablename__ = "product_branch"
    __table_args__ = (
        UniqueConstraint("product_id", "name", name="_product_branch_uc")
    )

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("product.id"))

    name = Column(String)
    disabled = Column(Boolean, default=False)
