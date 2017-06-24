# coding=utf-8
import re

from falcon import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound

from ultros_site.base_sink import BaseSink
from ultros_site.database.schema.builds import Product
from ultros_site.decorators import check_admin, add_csrf

__author__ = "Momo"


class EditProductRoute(BaseSink):
    route = re.compile(r"/admin/downloads/edit-product/(?P<product_id>\w+)")

    @check_admin
    @add_csrf
    def __call__(self, req, resp, product_id):
        db_session = req.context["db_session"]
        try:
            product = db_session.query(Product).filter_by(id=product_id).one()
        except NoResultFound:
            raise HTTPNotFound()
        else:
            self.render_template(
                req, resp, "admin/product_create.html",
                product=product
            )
