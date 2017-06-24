# coding=utf-8

from ultros_site.base_route import BaseRoute
from ultros_site.database.schema.product import Product
from ultros_site.decorators import add_csrf, check_admin

__author__ = "Momo"


class UsersRoute(BaseRoute):
    route = "/admin/products"

    @check_admin
    @add_csrf
    def on_get(self, req, resp):
        db_session = req.context["db_session"]
        products = db_session.query(Product).order_by(Product.order, Product.id).all()

        self.render_template(
            req, resp, "admin/products.html",
            products=products,
            csrf=resp.csrf
        )
