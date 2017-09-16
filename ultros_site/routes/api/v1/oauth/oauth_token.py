# coding=utf-8


import json
import logging
import secrets

from falcon import HTTPNotFound, HTTPBadRequest, HTTPUnauthorized
from sqlalchemy.orm.exc import NoResultFound

from ultros_site.base_route import BaseRoute
from ultros_site.database.schema.oauth_accesstoken import OauthAccessToken
from ultros_site.database.schema.oauth_application import OauthApplication
from ultros_site.database.schema.oauth_client import OauthClient
from ultros_site.decorators import render_api

__author__ = "Momo"
log = logging.getLogger("OAuth")



class OauthConfirmRoute(BaseRoute):
    route = "/api/v1/oauth/token"

    def on_get(self, req, resp):
        raise HTTPNotFound()

    @render_api
    def on_post(self, req, resp):
        if req.get_header("content-type") != "application/json":
            resp.status = "400 Bad Request"
            resp.content_type = "text"
            resp.body = "Data was not of type 'application/json'"
            return

        event_type = req.get_header("X-GitHub-Event")
        data = json.load(req.bounded_stream)
        db_session = req.context["db_session"]
        grant_type = data["grant_type"]
        client_id = data["client_id"]
        client_secret = data["client_secret"]
        redirect_uri = data["redirect_uri"]
        authorization_code = data["code"]

        if grant_type is None or client_id is None or client_secret is None or redirect_uri is None or authorization_code is None:
            resp.status = "400 Bad Request"
            resp.content_type = "text"
            resp.body = "Request was incomplete."
            return

        if grant_type != "authorization_code":
            resp.status = "400 Bad Request"
            resp.content_type = "text"
            resp.body = "grant_type must be 'authorization_code'"
            return

        # check if application is valid
        try:
            application = db_session.query(OauthApplication).filter_by(app_id=client_id).one()
        except NoResultFound:
            resp.status = "404 Not Found"
            resp.content_type = "text"
            resp.body = "Client ID is unknown."
            return

        try:
            client = db_session.query(OauthClient).filter_by(application_id=client_id, authorization_code=authorization_code).one()
        except NoResultFound:
            resp.status = "401 Unauthorized"
            resp.content_type = "text"
            resp.body = "Invalid authorization code."
            return

        if application.app_secret != client_secret:
            resp.status = "401 Unauthorized"
            resp.content_type = "text"
            resp.body = "Invalid client secret."
            return


        # create token
        token = secrets.token_urlsafe(32)
        token_entry = OauthAccessToken(
            token=token,
            user=client.user,
            scopes=client.scopes
        )
        db_session.delete(client)
        db_session.add(token_entry)
        return {
            "token_type": "Bearer",
            "access_token": token
        }
