# coding=utf-8
from ultros_site.base_route import BaseRoute
from ultros_site.decorators import check_admin

__author__ = "Gareth Coles"


class IndexRoute(BaseRoute):
    route = "/admin/celery"

    @check_admin
    def on_get(self, req, resp):
        self.render_template(
            req, resp, "admin/celery.html",
        )
