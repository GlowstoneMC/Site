# coding=utf-8
from ultros_site.base_route import BaseRoute

__author__ = "Gareth Coles"


class DocsRoute(BaseRoute):
    route = "/docs/api"

    def on_get(self, req, resp):
        self.render_template(
            req, resp, "api_docs.html",
        )
