# coding=utf-8

from falcon import HTTPTemporaryRedirect

from ultros_site.base_sink import BaseSink
from ultros_site.database.schema.builds import Product

__author__ = "Momo"


class DownloadsViewRoute(BaseSink):
    route = "/downloads"

    def __call__(self, req, resp):
        db_session = req.context["db_session"]
        products_count = db_session.query(Product).count()
        if products_count == 0:
            raise HTTPTemporaryRedirect("/")
        else:
            products = db_session.query(Product).order_by(Product.index)[0:products_count]
            default_product = products[0]
            raise HTTPTemporaryRedirect("/downloads/" + default_product.id)
