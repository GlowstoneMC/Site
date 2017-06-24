# coding=utf-8
from falcon import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound

from ultros_site.base_route import BaseRoute
from ultros_site.database.schema.product import Product
from ultros_site.decorators import check_admin, add_csrf

__author__ = "Momo"


class EditProductRoute(BaseRoute):
    route = "/admin/products/edit"

    @check_admin
    @add_csrf
    def on_get(self, req, resp):
        db_session = req.context["db_session"]
        params = {}

        if not req.get_param("product", store=params):
            raise HTTPNotFound()

        try:
            product = db_session.query(Product).filter_by(id=int(params["product"])).one()
        except NoResultFound:
            raise HTTPNotFound()
        else:
            self.render_template(
                req, resp, "admin/product_create.html",
                product=product
            )
