# coding=utf-8
from falcon import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound

from ultros_site.base_route import BaseRoute
from ultros_site.database.schema.oauth_application import OauthApplication
from ultros_site.decorators import add_csrf

__author__ = "Momo"


class OauthLoginRoute(BaseRoute):
    route = "/login/oauth"

    @add_csrf
    def on_get(self, req, resp):
        db_session = req.context["db_session"]
        # this is a request to get an authorization code
        # the request should include params:
        #   - response_type=code
        #   - client_id (application ID)
        #   - redirect_uri (optional)
        #   - scope (optional)

        response_type = req.get_param("response_type")
        if not response_type == "code":
            raise HTTPNotFound()

        client_id = req.get_param("client_id")
        if not client_id:
            raise HTTPNotFound()

        # validate existence of application using client_id
        try:
            application = db_session.query(OauthApplication).filter_by(app_id=client_id).one()
        except NoResultFound:
            raise HTTPNotFound()

        scopes = req.get_param_as_list("scope")
        redirect_uri = req.get_param("redirect_uri")
        oauth_state = req.get_param("state")

        if not scopes:
            scopes = application.scopes
        else:
            # validate if specified scopes are allowed with application
            for scope in scopes:
                if scope not in application.scopes:
                    # raise HTTPBadRequest('Scope "{}" is not allowed for this application'.format(scope))
                    pass

        if not redirect_uri:
            redirect_uri = application.redirect_uri

        if not oauth_state:
            oauth_state = ""

        self.render_template(
            req, resp, "login.html",
            csrf=resp.csrf,
            oauth=True,
            application=application,
            redirect_uri=redirect_uri,
            oauth_state=oauth_state,
            scopes=scopes
        )

    def on_post(self, req, resp):
        params = {}
