# coding=utf-8
import re

from falcon.errors import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound

from ultros_site.base_sink import BaseSink
from ultros_site.database.schema.product import Product

__author__ = "Momo"


class DownloadsViewRoute(BaseSink):
    route = re.compile(r"/downloads/(?P<product_id>\w+)")

    def __call__(self, req, resp, product_id):
        db_session = req.context["db_session"]
        try:
            product = db_session.query(Product).filter_by(id=int(product_id)).one()
        except NoResultFound:
            raise HTTPNotFound()
        else:
            products = db_session.query(Product).order_by(Product.order, Product.id).all()

            return self.render_template(
                req, resp, "downloads/index.html",
                product=product,
                products=products
            )
