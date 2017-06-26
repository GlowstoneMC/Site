# coding=utf-8
import json
from email.utils import format_datetime

from dicttoxml import dicttoxml
from ruamel import yaml

from ultros_site.utils import format_date_frontend

__author__ = "Gareth Coles"


class BaseSink:
    route = "/"

    def __init__(self, manager):
        self.manager = manager

    @property
    def db(self):
        return self.manager.database

    def get_args(self) -> tuple:
        return (
            self,
            self.route
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

    def render_api(self, req, resp, data):
        accepts = req.get_header("Accepts")

        if not accepts:
            accepts = "application/json"

        accepts = accepts.lower()

        if accepts == "application/x-yaml":
            resp.content_type = accepts
            resp.body = yaml.safe_dump(data)
        elif accepts == "application/json":
            resp.content_type = accepts
            resp.body = json.dumps(data)
        elif accepts == "application/xml":
            resp.content_type = accepts
            resp.body = dicttoxml(data)
        else:
            resp.status = "400 Bad Request"
            resp.content_type = "text"
            resp.body = "Unknown or unsupported content type: {}\n\n" \
                        "We support application/json, application/xml or application/x-yaml".format(accepts)

