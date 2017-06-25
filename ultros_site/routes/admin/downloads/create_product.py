# coding=utf-8
from sqlalchemy.orm.exc import NoResultFound

from ultros_site.base_route import BaseRoute
from ultros_site.database.schema.product import Product
from ultros_site.decorators import check_admin, add_csrf, check_csrf
from ultros_site.message import Message

__author__ = "Momo"


class CreateProductRoute(BaseRoute):
    route = "/admin/products/create"

    @check_admin
    @add_csrf
    def on_get(self, req, resp):
        self.render_template(
            req, resp, "admin/product_create.html",
            product=None
        )

    @check_admin
    @check_csrf
    @add_csrf
    def on_post(self, req, resp):
        params = {}
        db_session = req.context["db_session"]

        if not req.get_param("product_name", store=params) \
                or not req.get_param("product_order", store=params) \
                or not req.get_param("github_url", store=params) \
                or not req.get_param("circleci_url", store=params) \
                or not req.get_param("visibility", store=params):

            if req.get_param("product_id", store=params):
                resp.append_header("Refresh", "/admin/products/edit?product={}".format(params["product_id"]))

                return self.render_template(
                    req, resp, "admin/message_gate.html",
                    gate_message=Message("danger", "Missing input", "Please fill out the entire form"),
                    redirect_uri="/admin/products/edit?product={}".format(params["product_id"])
                )

            resp.append_header("Refresh", "/admin/products/create")

            return self.render_template(
                req, resp, "admin/message_gate.html",
                gate_message=Message("danger", "Missing input", "Please fill out the entire form"),
                redirect_uri="/admin/products/create"
            )

        resp.append_header("Refresh", "5;url=/admin/products")

        if not req.get_param("product_id", store=params):
            product = Product(
                name=params["product_name"], order=params["product_order"], hidden=params["visibility"] == "Hidden",
                url_github=params["github_url"], url_circleci=params["circleci_url"], branches=[]
            )
            db_session.add(product)

            return self.render_template(
                req, resp, "admin/message_gate.html",
                gate_message=Message(
                    "info", "Product created", "Your product has been created."
                ),
                redirect_uri="/admin/products"
            )

        try:
            product = db_session.query(Product).filter_by(id=int(params["product_id"])).one()
        except NoResultFound:
            return self.render_template(
                req, resp, "admin/message_gate.html",
                gate_message=Message(
                    "danger", "Error", "No such product: {}".format(params["post_id"])
                ),
                redirect_uri="/admin/products"
            )
        else:
            product.name = params["product_name"]
            product.order = int(params["product_order"])
            product.hidden = params["visibility"] == "Hidden"
            product.url_github = params["github_url"]
            product.url_circleci = params["circleci_url"]

            return self.render_template(
                req, resp, "admin/message_gate.html",
                gate_message=Message(
                    "info", "Product edited", "Your product has been edited."
                ),
                redirect_uri="/admin/products"
            )
