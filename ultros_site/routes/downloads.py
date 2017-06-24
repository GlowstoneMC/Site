# coding=utf-8

from falcon import HTTPTemporaryRedirect

from ultros_site.base_route import BaseRoute
from ultros_site.database.schema.product import Product

__author__ = "Momo"


class DownloadsViewRoute(BaseRoute):
    route = "/downloads"

    def on_get(self, req, resp):
        db_session = req.context["db_session"]
        products_count = db_session.query(Product).count()

        if products_count == 0:
            raise HTTPTemporaryRedirect("/")
        else:
            products = db_session.query(Product).order_by(Product.order, Product.id).all()
            default_product = products[0]

            raise HTTPTemporaryRedirect("/downloads/{}".format(default_product.id))
