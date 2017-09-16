# coding=utf-8
import base64
import datetime
import hashlib
import secrets

import bcrypt
from sqlalchemy.orm.exc import NoResultFound

from ultros_site.base_route import BaseRoute
from ultros_site.database.schema.session import Session
from ultros_site.database.schema.user import User
from ultros_site.decorators import check_csrf, add_csrf
from ultros_site.message import Message

__author__ = "Gareth Coles"


class LoginRoute(BaseRoute):
    route = "/login"

    @add_csrf
    def on_get(self, req, resp):
        if req.context["user"]:
            resp.append_header("Refresh", "5;url=/profile")
            return self.render_template(
                req, resp, "message_gate.html",
                gate_message=Message(
                    "danger", "Already logged in",
                    "You're already logged in!"
                ),
                redirect_uri="/profile"
            )

        self.render_template(
            req, resp,
            "login.html", error=None, csrf=resp.csrf
        )

    @check_csrf
    @add_csrf
    def on_post(self, req, resp):
        params = {}

        if not req.get_param("username", store=params) or not req.get_param("password", store=params):
            return self.render_template(
                req, resp, "login.html",
                message=Message("danger", "Login failed", "Please enter both a username and password."),
                csrf=resp.csrf
            )

        params["password"] = base64.b64encode(hashlib.sha256(params["password"].encode("utf-8")).digest())

        db_session = req.context["db_session"]

        try:
            user = db_session.query(User).filter_by(username=params["username"]).one()
        except NoResultFound:
            return self.render_template(
                req, resp, "login.html",
                message=Message("danger", "Login failed", "Incorrect username or password - please try again."),
                csrf=resp.csrf
            )
        else:
            if not bcrypt.checkpw(params["password"], user.password.encode("UTF-8")):
                return self.render_template(
                    req, resp, "login.html",
                    message=Message("danger", "Login failed", "Incorrect username or password - please try again."),
                    csrf=resp.csrf
                )
            if not user.email_verified:
                return self.render_template(
                    req, resp, "login.html",
                    message=Message(
                        "danger",
                        "Login failed",
                        "This user account has not been verified - please check your email for more information, or "
                        "contact one of the developers for help."
                    ),
                    csrf=resp.csrf
                )
            # Login is OK!
            token = secrets.token_urlsafe(24)
            expires = datetime.datetime.now() + datetime.timedelta(days=30)
            age = (expires - datetime.datetime.now()).seconds

            session = Session(user=user, token=token, expires=expires, awaiting_mfa=user.mfa_enabled)
            db_session.add(session)

            resp.set_cookie("token", token, max_age=age, secure=False, path="/")
            req.context["user"] = user

            if not user.mfa_enabled:
                resp.append_header("Refresh", "5;url=/")

                return self.render_template(
                    req, resp, "message_gate.html",
                    gate_message=Message("info", "Logged in", "You have been logged in successfully."),
                    redirect_uri="/"
                )
            else:
                return self.render_template(req, resp, "mfa/challenge.html")
