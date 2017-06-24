# coding=utf-8
import re

from sqlalchemy.orm.exc import NoResultFound

from ultros_site.base_sink import BaseSink
from ultros_site.database.schema.product import Product
from ultros_site.decorators import check_admin, check_csrf
from ultros_site.message import Message

__author__ = "Momo"


class DeleteProductRoute(BaseSink):
    route = re.compile(r"/admin/products/delete/(?P<product_id>\w+)")

    @check_admin
    @check_csrf
    def __call__(self, req, resp, product_id):
        db_session = req.context["db_session"]
        resp.append_header("Refresh", "5;url=/admin/products")

        try:
            product = db_session.query(Product).filter_by(id=int(product_id)).one()
        except NoResultFound:
            return self.render_template(
                req, resp, "admin/message_gate.html",
                gate_message=Message(
                    "danger", "Error", "No such product: {}".format(product_id)
                ),
                redirect_uri="/admin/products"
            )
        else:
            db_session.delete(product)

        return self.render_template(
            req, resp, "admin/message_gate.html",
            gate_message=Message(
                "info", "Product deleted", "Product has been deleted."
            ),
            redirect_uri="/admin/products"
        )
