# coding=utf-8
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship

# Imported so it loads first for the relationship below
from ultros_site.database.schema.product_branch import ProductBranch  # noqa: F401
from ultros_site.database.common import DeclarativeBase

__author__ = "Momo"


class Product(DeclarativeBase):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    order = Column(Integer, default=1)
    hidden = Column(Boolean)

    url_github = Column(String, unique=True)
    url_circleci = Column(String, unique=True)

    branches = relationship("ProductBranch", secondary="product_branch_association")

    default_branch_id = Column(Integer, ForeignKey("product_branch.id"))
    default_branch = relationship("ProductBranch", foreign_keys=[default_branch_id])

    builds = relationship("ProductBuild", back_populates="product", cascade="all, delete, delete-orphan")

    def __repr__(self):
        return "<{}(name={}>".format(
            self.__class__.__name__,
            self.name
        )
