# coding=utf-8
import secrets

from falcon.errors import HTTPBadRequest
from ultros_site.base_route import BaseRoute
from ultros_site.database.schema.api_key import APIKey
from ultros_site.decorators import add_csrf, check_csrf
from ultros_site.message import Message

__author__ = "Gareth Coles"


class ProfileRoute(BaseRoute):
    route = "/profile/api_keys"

    @add_csrf
    def on_get(self, req, resp):
        user = req.context["user"]

        if not user:
            raise HTTPBadRequest()

        if not user.api_enabled:
            resp.append_header("Refresh", "5;url=/profile")

            return self.render_template(
                req, resp, "message_gate.html",
                gate_message=Message(
                    "danger", "No access",
                    "You don't have API access - please contact a member of staff if you need it."
                ),
                redirect_uri="/"
            )

        db_session = req.context["db_session"]
        keys = {}

        for key in db_session.query(APIKey).filter_by(user_id=user.id).all():
            keys[key.key] = key.name

        self.render_template(
            req, resp, "users/api_keys.html",
            user=user,
            keys=keys
        )

    @check_csrf
    @add_csrf
    def on_post(self, req, resp):
        params = {}

        user = req.context["user"]
        db_session = req.context["db_session"]

        keys = {}

        if not user:
            raise HTTPBadRequest()

        if not user.api_enabled:
            resp.append_header("Refresh", "5;url=/profile")

            return self.render_template(
                req, resp, "message_gate.html",
                gate_message=Message(
                    "danger", "No access",
                    "You don't have API access - please contact a member of staff if you need it."
                ),
                redirect_uri="/"
            )

        for key in db_session.query(APIKey).filter_by(user_id=user.id).all():
            keys[key.key] = key.name

        if not req.get_param("action", store=params):
            raise HTTPBadRequest()

        if params["action"] == "create":
            if len(keys) >= 10:
                return self.render_template(
                    req, resp, "users/api_keys.html",
                    user=user,
                    keys=keys,
                    message=Message(
                        "danger", "Too many keys",
                        "You already have 10 api keys! If you need more, contact staff directly."
                    )
                )

            if not req.get_param("name", store=params) or not params["name"]:
                return self.render_template(
                    req, resp, "users/api_keys.html",
                    user=user,
                    keys=keys,
                    message=Message(
                        "danger", "Missing name",
                        "Please supply a name for your new API key"
                    )
                )

            new_key = APIKey(user=user, name=params["name"], key=secrets.token_urlsafe(32))
            db_session.add(new_key)

            keys[new_key.key] = new_key.name

            return self.render_template(
                req, resp, "users/api_keys.html",
                user=user,
                keys=keys,
                message=Message(
                    "success", "Key created",
                    "New API key \"{}\" created successfully.".format(new_key.name)
                )
            )
        elif params["action"] == "delete":
            if not req.get_param("key", store=params):
                raise HTTPBadRequest()

            if params["key"] not in keys:
                return self.render_template(
                    req, resp, "users/api_keys.html",
                    user=user,
                    keys=keys,
                    message=Message(
                        "danger", "No such key",
                        "Unknown key: {}.".format(params["key"])
                    )
                )

            old_key = db_session.query(APIKey).filter_by(key=params["key"]).one()
            db_session.delete(old_key)
            del keys[params["key"]]

            return self.render_template(
                req, resp, "users/api_keys.html",
                user=user,
                keys=keys,
                message=Message(
                    "success", "Key deleted",
                    "API key \"{}\" deleted successfully.".format(old_key.name)
                )
            )
        else:
            raise HTTPBadRequest()
