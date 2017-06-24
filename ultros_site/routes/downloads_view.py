# coding=utf-8
import re

from falcon.errors import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound

from ultros_site.base_sink import BaseSink
from ultros_site.database.schema.builds import Product

__author__ = "Momo"


class DownloadsViewRoute(BaseSink):
    route = re.compile(r"/downloads/(?P<product_id>\w+)")

    def __call__(self, req, resp, product_id):
        db_session = req.context["db_session"]
        try:
            product = db_session.query(Product).filter_by(id=product_id).one()
        except NoResultFound:
            raise HTTPNotFound()
        else:
            products_count = db_session.query(Product).count()
            products = db_session.query(Product).order_by(Product.index)[0:products_count]
            return self.render_template(
                req, resp, "builds/downloads.html",
                product=product,
                products=products
            )
