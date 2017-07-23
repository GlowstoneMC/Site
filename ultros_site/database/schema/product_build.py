# coding=utf-8
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime, BigInteger, UniqueConstraint
from sqlalchemy.orm import relationship

# Imported so it loads first for the relationship below
from ultros_site.database.schema.product_branch import ProductBranch  # noqa: F401
from ultros_site.database.common import DeclarativeBase

__author__ = "Gareth Coles"


class ProductBuild(DeclarativeBase):
    __tablename__ = "product_build"
    __table_args__ = (
        UniqueConstraint("num", "product_id", "branch_id", name="_product_build_uc"),
    )

    id = Column(Integer, primary_key=True)
    num = Column(Integer)

    release = Column(Boolean)
    success = Column(Boolean)
    state_text = Column(String)

    commit_url = Column(String)
    commit_message = Column(String)

    date = Column(DateTime)
    downloads = Column(BigInteger)

    file_path = Column(String, unique=True)
    url_circleci = Column(String, unique=True)

    branch_id = Column(Integer, ForeignKey("product_branch.id"))
    product_id = Column(Integer, ForeignKey("product.id"))

    branch = relationship("ProductBranch", back_populates="builds")
    product = relationship("Product", back_populates="builds")

    def __repr__(self):
        return "<{}(num={}, product={}, branch={}>".format(
            self.__class__.__name__,
            self.num, self.product.name, self.branch.name
        )
