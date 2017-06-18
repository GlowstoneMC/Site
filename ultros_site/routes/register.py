# coding=utf-8
import base64
import datetime
import hashlib
import secrets

import bcrypt

from requests import Session
from sqlalchemy.orm.exc import NoResultFound

from ultros_site.base_route import BaseRoute
from ultros_site.database.schema.email_code import EmailCode
from ultros_site.database.schema.user import User
from ultros_site.decorators import check_csrf, add_csrf
from ultros_site.message import Message
from ultros_site.tasks.__main__ import app as celery

__author__ = "Gareth Coles"
RECAPTCHA_URL = "https://www.google.com/recaptcha/api/siteverify"


class RegisterRoute(BaseRoute):
    route = "/login/register"

    @add_csrf
    def on_get(self, req, resp):
        if req.context["user"]:
            resp.append_header("Refresh", "5;url=/")
            return self.render_template(
                req, resp, "message_gate.html",
                gate_message=Message(
                    "danger", "Already logged in",
                    "You're already logged in!"
                ),
                redirect_uri="/"
            )

        self.render_template(
            req, resp,
            "register.html", error=None, csrf=resp.csrf
        )

    @check_csrf
    @add_csrf
    def on_post(self, req, resp):
        if req.context["user"]:
            resp.append_header("Refresh", "5;url=/")
            return self.render_template(
                req, resp, "message_gate.html",
                gate_message=Message(
                    "danger", "Already logged in",
                    "You're already logged in!"
                ),
                redirect_uri="/"
            )

        params = {}

        if not req.get_param("g-recaptcha-response", store=params):
            return self.render_template(
                req, resp, "register.html",
                message=Message(
                    "danger", "Failed CAPTCHA",
                    "Unfortunately, we were not able to verify you by CAPTCHA. Please try again."
                ),
                csrf=resp.csrf
            )

        http = Session()
        captcha_response = http.post(
            RECAPTCHA_URL, data={
                "secret": self.manager.database.config["recaptcha_secret"],
                "response": params["g-recaptcha-response"]
            }
        ).json()

        if not captcha_response["success"]:
            return self.render_template(
                req, resp, "register.html",
                message=Message(
                    "danger", "Failed CAPTCHA",
                    "Unfortunately, we were not able to verify you by CAPTCHA. Please try again."
                ),
                csrf=resp.csrf
            )

        if not req.get_param("username", store=params) \
                or not req.get_param("email", store=params) \
                or not req.get_param("password", store=params) \
                or not req.get_param("confirm_password", store=params):

            return self.render_template(
                req, resp, "register.html",
                message=Message("danger", "Missing input", "Please fill out the entire form"),
                csrf=resp.csrf
            )

        if not params["password"] == params["confirm_password"]:
            return self.render_template(
                req, resp, "register.html",
                message=Message("danger", "Passwords do not match", "Please ensure that your passwords match"),
                csrf=resp.csrf
            )

        db_session = req.context["db_session"]

        try:
            db_session.query(User).filter_by(username=params["username"]).one()
        except NoResultFound:
            pass
        else:
            return self.render_template(
                req, resp, "register.html",
                message=Message("danger", "User already exists", "That username is already taken - please try another"),
                csrf=resp.csrf
            )

        try:
            db_session.query(User).filter_by(email=params["email"]).one()
        except NoResultFound:
            pass
        else:
            return self.render_template(
                req, resp, "register.html",
                message=Message("danger", "Email already used", "An account already exists for that email address"),
                csrf=resp.csrf
            )

        password = base64.b64encode(hashlib.sha256(params["password"].encode("utf-8")).digest())
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode("utf-8")

        user = User(
            username=params["username"], password=hashed_password, created=datetime.datetime.now(),
            email=params["email"], email_verified=not self.db.config["email"]["use"],
            admin=(params["username"] == self.manager.database.config["admin_username"])
        )

        db_session.add(user)

        resp.append_header("Refresh", "10;url=/")

        if self.db.config["email"]["use"]:
            key = secrets.token_urlsafe(32)
            email_code = EmailCode(
                user=user, code=key
            )

            db_session.add(email_code)

            celery.send_task(
                "send_email",
                args=["email_verification", user.email, "Email verification"],
                kwargs={"verify_url": "/login/verify/{}".format(key)}
            )

            return self.render_template(
                req, resp, "message_gate.html",
                gate_message=Message(
                    "info", "Registered", "Your account has been registered - please check your email to verify it!"
                ),
                redirect_uri="/"
            )

        return self.render_template(
            req, resp, "message_gate.html",
            gate_message=Message(
                "info", "Registered", "Your account has been registered successfully."
            ),
            redirect_uri="/"
        )
