# coding=utf-8
from ultros_site.base_route import BaseRoute

__author__ = "Gareth Coles"


class SettingsRoute(BaseRoute):
    route = "/settings"

    def on_get(self, req, resp):
        self.render_template(
            req, resp, "users/settings.html"
        )
