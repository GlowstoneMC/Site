# coding=utf-8

from falcon import HTTPNotFound, HTTPTemporaryRedirect
from sqlalchemy.orm.exc import NoResultFound

from ultros_site.base_route import BaseRoute

from ultros_site.database.schema.product import Product
from ultros_site.decorators import check_admin, add_csrf

from ultros_site.tasks.__main__ import app as celery

__author__ = "Momo"


class ImportBranchesRoute(BaseRoute):
    route = "/admin/products/import"

    def callback_import(self, product, data):
        print("called back")

    @check_admin
    @add_csrf
    def on_get(self, req, resp):
        db_session = req.context["db_session"]
        params = {}

        if not req.get_param("product", store=params):
            raise HTTPNotFound()

        try:
            product = db_session.query(Product).filter_by(id=int(params["product"])).one()

        except NoResultFound:
            raise HTTPNotFound()
        else:
            celery.send_task(
                "github_import",
                args=[product.id, "GlowstoneMC", product.name],
                kwargs={}
            )

            raise HTTPTemporaryRedirect("/admin/products/")
