# coding=utf-8
import base64
import hashlib
import secrets
from io import BytesIO

import bcrypt
import pyotp
import qrcode
from falcon import HTTPBadRequest

from ultros_site.base_route import BaseRoute
from ultros_site.database.schema.backup_code import BackupCode
from ultros_site.decorators import add_csrf, check_csrf
from ultros_site.message import Message
from ultros_site.tasks.__main__ import app as celery

__author__ = "Gareth Coles"


class MFASetupRoute(BaseRoute):
    route = "/mfa/setup"

    @add_csrf
    def on_get(self, req, resp):
        if not req.context["user"]:
            raise HTTPBadRequest()

        self.render_template(
            req, resp, "mfa/setup/step_one.html"
        )

    @check_csrf
    @add_csrf
    def on_post(self, req, resp):
        step = req.get_param("step")

        if step == "one":
            return self.step_one(req, resp)
        elif step == "two":
            return self.step_two(req, resp)
        else:
            raise HTTPBadRequest()

    def step_one(self, req, resp):
        password = req.get_param("password")
        user = req.context["user"]

        if not password:
            return self.render_template(
                req, resp, "mfa/setup/step_one.html",
                message=Message(
                    "danger", "Missing Password",
                    "Please enter your password to continue."
                )
            )

        password = base64.b64encode(
            hashlib.sha256(password.encode("utf-8")).digest()
        )

        if not bcrypt.checkpw(password, user.password.encode("UTF-8")):
            return self.render_template(
                req, resp, "mfa/setup/step_one.html",
                message=Message(
                    "danger", "Incorrect Password",
                    "The password you entered was incorrect."
                )
            )

        user.mfa_token = pyotp.random_base32()
        totp = pyotp.TOTP(user.mfa_token)
        uri = totp.provisioning_uri("{}@glowstone.net".format(user.username), issuer_name="Glowstone")

        image = qrcode.make(uri)
        buffer = BytesIO()

        image.save(buffer, format="PNG")
        qr_code = base64.b64encode(buffer.getvalue()).decode("UTF-8")

        return self.render_template(
            req, resp, "mfa/setup/step_two.html",
            qr_code=qr_code
        )

    def step_two(self, req, resp):
        user = req.context["user"]
        totp = pyotp.TOTP(user.mfa_token)
        code = req.get_param("code")
        db_session = req.context["db_session"]

        if not code:
            uri = totp.provisioning_uri("{}@glowstone.net".format(user.username), issuer_name="Glowstone")

            image = qrcode.make(uri)
            buffer = BytesIO()

            image.save(buffer, format="PNG")
            qr_code = base64.b64encode(buffer.getvalue()).decode("UTF-8")

            return self.render_template(
                req, resp, "mfa/setup/step_two.html",
                message=Message(
                    "danger", "Missing code",
                    "Please enter a code from your authenticator application to continue."
                ),
                qr_code=qr_code
            )

        if totp.verify(code):
            backup_codes = []

            for i in range(10):
                token = secrets.token_urlsafe(24)
                db_session.add(BackupCode(user=user, code=token))
                backup_codes.append(token)

            celery.send_task(
                "send_email",
                args=["backup_codes", user.email, "MFA backup codes"],
                kwargs={"codes": backup_codes}
            )

            user.mfa_enabled = True

            return self.render_template(
                req, resp, "mfa/setup/complete.html"
            )
        else:
            uri = totp.provisioning_uri("{}@glowstone.net".format(user.username), issuer_name="Glowstone")

            image = qrcode.make(uri)
            buffer = BytesIO()

            image.save(buffer, format="PNG")
            qr_code = base64.b64encode(buffer.getvalue()).decode("UTF-8")

            return self.render_template(
                req, resp, "mfa/setup/step_two.html",
                message=Message(
                    "danger", "Invalid code",
                    "The auth code you provided was invalid - please try again."
                ),
                qr_code=qr_code
            )
