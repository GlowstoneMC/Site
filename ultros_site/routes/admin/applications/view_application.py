# coding=utf-8
from falcon import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound

from ultros_site.base_route import BaseRoute
from ultros_site.database.schema.oauth_application import OauthApplication
from ultros_site.decorators import add_csrf, check_admin

__author__ = "Momo"


class ApplicationViewRoute(BaseRoute):
    route = "/admin/applications/view"

    @check_admin
    @add_csrf
    def on_get(self, req, resp):
        application_id = req.get_param("id")
        if not application_id:
            raise HTTPNotFound()
        db_session = req.context["db_session"]
        try:
            application = db_session.query(OauthApplication).filter_by(id=application_id).one()
        except NoResultFound:
            raise HTTPNotFound()

        self.render_template(
            req, resp, "admin/application_view.html",
            application=application,
            scopes=['user:username', 'user:email', 'user:profile'],
            csrf=resp.csrf
        )
