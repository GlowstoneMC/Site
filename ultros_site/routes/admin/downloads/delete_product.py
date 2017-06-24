# coding=utf-8
import re

from falcon import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound

from ultros_site.base_sink import BaseSink
from ultros_site.database.schema.builds import Product
from ultros_site.decorators import check_admin, check_csrf
from ultros_site.message import Message

__author__ = "Momo"


class DeleteProductRoute(BaseSink):
    route = re.compile(r"/admin/downloads/delete-product/(?P<product_id>\w+)")

    @check_admin
    @check_csrf
    def __call__(self, req, resp, product_id):
        db_session = req.context["db_session"]

        resp.append_header("Refresh", "5;url=/admin/downloads")
        try:
            product = db_session.query(Product).filter_by(id=product_id).one()
        except NoResultFound:
            raise HTTPNotFound()
        else:
            db_session.delete(product)
        return self.render_template(
            req, resp, "admin/message_gate.html",
            gate_message=Message(
                "info", "Product deleted", "Product has been deleted."
            ),
            redirect_uri="/admin/downloads"
        )
