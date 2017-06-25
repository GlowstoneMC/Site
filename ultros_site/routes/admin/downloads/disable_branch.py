# coding=utf-8
from falcon import HTTPNotFound, HTTPTemporaryRedirect
from sqlalchemy.orm.exc import NoResultFound

from ultros_site.base_route import BaseRoute
from ultros_site.database.schema.product import Product
from ultros_site.database.schema.product_branch import ProductBranch
from ultros_site.decorators import check_admin, add_csrf

__author__ = "Momo"


class DisableBranchRoute(BaseRoute):
    route = "/admin/branch/disable"

    @check_admin
    @add_csrf
    def on_get(self, req, resp):
        db_session = req.context["db_session"]
        params = {}

        if not req.get_param("product", store=params) \
                or not req.get_param("branch", store=params):
            raise HTTPNotFound()

        try:
            product = db_session.query(Product).filter_by(id=int(params["product"])).one()
            branch = db_session.query(ProductBranch).filter_by(id=int(params["branch"])).one()
        except NoResultFound:
            raise HTTPNotFound()
        else:
            branch.disabled = True
            db_session.commit()
            raise HTTPTemporaryRedirect(str.format("/admin/products/configure?product={}", product.id))
