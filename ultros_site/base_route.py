# coding=utf-8
from email.utils import format_datetime

from ultros_site.utils import format_date_frontend

__author__ = "Gareth Coles"


class BaseRoute:
    route = "/"

    def __init__(self, manager):
        self.manager = manager

    @property
    def db(self):
        return self.manager.database

    def get_args(self) -> tuple:
        return (
            self.route,
            self
        )

    def render_template(self, req, resp, template, **kwargs):
        kwargs["_context"] = req.context
        kwargs["format_date"] = format_date_frontend
        kwargs["rfc2822"] = format_datetime

        if hasattr(resp, "csrf"):
            kwargs["csrf"] = resp.csrf

        content_type, body = self.manager.render_template(
            template, **kwargs
        )

        resp.content_type = content_type
        resp.body = body
