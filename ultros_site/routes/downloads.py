# coding=utf-8

from falcon import HTTPTemporaryRedirect

from ultros_site.base_route import BaseRoute
from ultros_site.database.schema.product import Product
from ultros_site.message import Message

__author__ = "Momo"


class DownloadsViewRoute(BaseRoute):
    route = "/downloads"

    def on_get(self, req, resp):
        db_session = req.context["db_session"]
        products_count = db_session.query(Product).count()

        if products_count == 0:
            resp.append_header("Refresh", "10;url=/")

            return self.render_template(
                req, resp, "message_gate.html",
                gate_message=Message(
                    "danger", "WIP", "The downloads area is under construction. Come back later!"
                ),
                redirect_uri="/"
            )
        else:
            products = db_session.query(Product).order_by(Product.order, Product.id).all()
            default_product = products[0]

            raise HTTPTemporaryRedirect("/downloads/{}".format(default_product.id))
