# coding=utf-8

import secrets
from urllib.parse import urlparse, urlencode

from falcon import HTTPNotFound, HTTPBadRequest
from sqlalchemy.orm.exc import NoResultFound

from ultros_site.base_route import BaseRoute
from ultros_site.database.schema.oauth_application import OauthApplication
from ultros_site.database.schema.oauth_client import OauthClient
from ultros_site.decorators import add_csrf, check_csrf
from ultros_site.message import Message

__author__ = "Momo"


class OauthConfirmRoute(BaseRoute):
    route = "/oauth/confirm"

    def on_get(self, req, resp):
        raise HTTPNotFound()

    @check_csrf
    @add_csrf
    def on_post(self, req, resp):
        user = req.context["user"]
        db_session = req.context["db_session"]
        redirect_uri = req.get_param("redirect_uri")
        state = req.get_param("state")
        application_id = req.get_param("application")
        # check if everything is there

        if user is None or redirect_uri is None or application_id is None:
            raise HTTPBadRequest()

        # check if application is valid
        try:
            application = db_session.query(OauthApplication).filter_by(app_id=application_id).one()
        except NoResultFound:
            raise HTTPNotFound()

        # create OAuth client
        authorization_code = secrets.token_urlsafe(32)
        client = OauthClient(
            user=user,
            application_id=application_id,
            redirect_uri=redirect_uri,
            scopes=['user:username'],
            authorization_code=authorization_code
        )
        db_session.add(client)
        # add parameters to redirect URI
        params = {
            'code': authorization_code
        }
        if state is not None:
            params["state"] = state
        redirect_uri += ('&', '?')[urlparse(redirect_uri).query == ''] + urlencode(params)
        resp.append_header("Refresh", "5;url={}".format(redirect_uri))
        return self.render_template(
            req, resp, "message_gate.html",
            gate_message=Message("info", "Application access authorized",
                                 "You have authorized the application to access information about your account."
                                 "<br>"
                                 "You may revoke this access in your account settings at any time."),
            redirect_uri=redirect_uri
        )
