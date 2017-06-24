# coding=utf-8
from sqlalchemy.orm.exc import NoResultFound

from ultros_site.base_route import BaseRoute
from ultros_site.database.schema.builds import Product
from ultros_site.decorators import check_admin, add_csrf, check_csrf
from ultros_site.message import Message

__author__ = "Momo"


class CreateProductRoute(BaseRoute):
    route = "/admin/downloads/create-product"

    @check_admin
    @add_csrf
    def on_get(self, req, resp):
        self.render_template(
            req, resp, "admin/product_create.html",
            product=None
        )

    @check_admin
    @check_csrf
    def on_post(self, req, resp):
        params = {}
        db_session = req.context["db_session"]

        if not req.get_param("product_name", store=params) \
                or not req.get_param("github_url", store=params) \
                or not req.get_param("circleci_url", store=params) \
                or not req.get_param("visibility", store=params):
            return self.render_template(
                req, resp, "admin/product_create.html",
                message=Message("danger", "Missing input", "Please fill out the entire form"),
                csrf=resp.csrf
            )

        try:
            product = db_session.query(Product).filter_by(id=params["product_name"]).one()
        except NoResultFound:
            index = db_session.query(Product).count()
            product = Product(
                id=params["product_name"], index=index, hidden=params["visibility"] == "Hidden",
                url_github=params["github_url"], url_circleci=params["circleci_url"]
            )
            db_session.add(product)

            resp.append_header("Refresh", "5;url=/admin/downloads")

            return self.render_template(
                req, resp, "admin/message_gate.html",
                gate_message=Message(
                    "info", "Product created", "Your product has been created."
                ),
                redirect_uri="/admin/downloads"
            )
        else:
            # edit
            product.hidden = params["visibility"] == "Hidden"
            product.url_github = params["github_url"]
            product.url_circleci = params["circleci_url"]
            resp.append_header("Refresh", "5;url=/admin/downloads")
            return self.render_template(
                req, resp, "admin/message_gate.html",
                gate_message=Message(
                    "info", "Product edited", "Your product has been edited."
                ),
                redirect_uri="/admin/downloads"
            )
