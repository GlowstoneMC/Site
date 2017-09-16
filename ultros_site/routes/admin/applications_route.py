# coding=utf-8
from sqlalchemy import func

from ultros_site.base_route import BaseRoute
from ultros_site.database.schema.oauth_application import OauthApplication
from ultros_site.decorators import check_admin, add_csrf

__author__ = "Momo"


class ApplicationsRoute(BaseRoute):
    route = "/admin/applications"

    @check_admin
    @add_csrf
    def on_get(self, req, resp):
        page = req.get_param_as_int("page") or 1
        first_index = (page - 1) * 10
        last_index = page * 10

        db_session = req.context["db_session"]
        applications = db_session.query(OauthApplication).order_by(OauthApplication.id)[first_index:last_index]
        count = db_session.query(func.count(OauthApplication.id)).scalar()
        pages = int(count / 10)

        if count % 10:
            pages += 1
        if pages < 1:
            pages = 1

        self.render_template(
            req, resp, "admin/applications.html",
            page=page,
            pages=pages,
            applications=applications,
            csrf=resp.csrf
        )
