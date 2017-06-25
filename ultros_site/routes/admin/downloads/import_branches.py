# coding=utf-8

from falcon import HTTPNotFound, HTTPTemporaryRedirect
from sqlalchemy.orm.exc import NoResultFound

from ultros_site.base_route import BaseRoute
from ultros_site.database.schema.product import Product
from ultros_site.decorators import check_admin, add_csrf
from ultros_site.tasks.__main__ import app as celery

__author__ = "Momo"


class EnableBranchRoute(BaseRoute):
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
            # todo: GH-organization, GH-API user and token need to be configurable (token only needs "repo" permissions)
            celery.send_task(
                "github_import",
                args=[self.callback_import, product, [], "GlowstoneMC", product.name, "<gh user>",
                      "<gh access token>"],
                kwargs={}
            )
            # endpoint = str.format("https://{}:{}@api.github.com/repos/{}/{}/branches", "xxx",
            #                      "xxx", "GlowstoneMC", product.name)
            # session = requests.session()
            # data = json.loads(session.get(endpoint).text)
            # for b in data:
            #    b_name = b["name"]
            #    print(b_name)
            raise HTTPTemporaryRedirect("/admin/products/")
