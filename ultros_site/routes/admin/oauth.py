# coding=utf-8
import re

import twython

from falcon import HTTPBadRequest
from sqlalchemy.orm.exc import NoResultFound

from ultros_site.base_sink import BaseSink
from ultros_site.database.schema.setting import Setting
from ultros_site.decorators import check_admin, check_csrf
from ultros_site.message import Message

__author__ = "Gareth Coles"
SERVICES = ["twitter"]
ACTIONS = ["link", "unlink", "auth"]

TWITTER_NEEDED_KEYS = ["twitter_app_key", "twitter_app_secret"]
TWITTER_OAUTH_KEYS = ["twitter_oauth_token", "twitter_oauth_token_secret"]


class SettingsRoute(BaseSink):
    route = re.compile("/admin/oauth/(?P<service>[^/]+)/(?P<action>[^/]+)")

    @check_admin
    def __call__(self, req, resp, service, action):
        if service not in SERVICES:
            raise HTTPBadRequest("Unknown service: {}".format(service))

        if action not in ACTIONS:
            raise HTTPBadRequest("Unknown action: {}".format(action))

        return getattr(self, "do_{}".format(action))(req, resp, service)

    def do_link(self, req, resp, service):
        db_session = req.context["db_session"]

        if service == "twitter":
            try:
                db_session.query(Setting).filter_by(key="twitter_username").one()
            except NoResultFound:
                pass  # Good!
            else:
                resp.append_header("Refresh", "5;url=/admin/settings")

                return self.render_template(
                    req, resp, "admin/message_gate.html",
                    gate_message=Message(
                        "warning", "Already linked", "A Twitter account is already linked - please unlink it first."
                    ),
                    redirect_uri="/admin/settings"
                )

            settings = {}

            db_settings = db_session.query(Setting).filter(Setting.key.startswith("twitter_")).all()

            for setting in db_settings:
                if setting.key in TWITTER_OAUTH_KEYS or setting.key == "twitter_username":
                    db_session.delete(setting)
                    continue

                settings[setting.key] = setting.value

            db_session.commit()

            for key in TWITTER_NEEDED_KEYS:
                if key not in settings:
                    resp.append_header("Refresh", "5;url=/admin/settings")

                    return self.render_template(
                        req, resp, "admin/message_gate.html",
                        gate_message=Message(
                            "danger", "Missing setting", "Setting missing: {}".format(key)
                        ),
                        redirect_uri="/admin/settings"
                    )

            twitter = twython.Twython(
                settings["twitter_app_key"], settings["twitter_app_secret"]
            )

            callback_url = "https://beta.glowstone.net/admin/oauth/twitter/auth"

            # "twitter_oauth_token", "twitter_oauth_token_secret"

            auth = twitter.get_authentication_tokens(callback_url=callback_url)

            db_session.add(Setting(key="twitter_oauth_token", value=auth["oauth_token"]))
            db_session.add(Setting(key="twitter_oauth_token_secret", value=auth["oauth_token_secret"]))

            resp.append_header("Refresh", "5;url={}".format(auth["auth_url"]))

            return self.render_template(
                req, resp, "admin/message_gate.html",
                gate_message=Message(
                    "info", "Redirecting...", "Redirecting you to Twitter..."
                ),
                redirect_uri=auth["auth_url"]
            )

    @check_csrf
    def do_unlink(self, req, resp, service):
        db_session = req.context["db_session"]

        if service == "twitter":
            try:
                db_session.query(Setting).filter_by(key="twitter_username").one()
            except NoResultFound:
                resp.append_header("Refresh", "5;url=/admin/settings")

                return self.render_template(
                    req, resp, "admin/message_gate.html",
                    gate_message=Message(
                        "warning", "No account linked", "No twitter account is currently linked."
                    ),
                    redirect_uri="/admin/settings"
                )
            else:
                db_settings = db_session.query(Setting).filter(Setting.key.startswith("twitter_")).all()

                for setting in db_settings:
                    if setting.key in TWITTER_OAUTH_KEYS or setting.key == "twitter_username":
                        db_session.delete(setting)
                        continue

                db_session.commit()

                resp.append_header("Refresh", "5;url=/admin/settings")

                return self.render_template(
                    req, resp, "admin/message_gate.html",
                    gate_message=Message(
                        "success", "Account unlinked", "The twitter account has been unlinked."
                    ),
                    redirect_uri="/admin/settings"
                )

    def do_auth(self, req, resp, service):
        db_session = req.context["db_session"]
        params = {}

        if service == "twitter":
            try:
                db_session.query(Setting).filter_by(key="twitter_username").one()
            except NoResultFound:
                pass  # Good!
            else:
                resp.append_header("Refresh", "5;url=/admin/settings")

                return self.render_template(
                    req, resp, "admin/message_gate.html",
                    gate_message=Message(
                        "warning", "Already linked", "A Twitter account is already linked - please unlink it first."
                    ),
                    redirect_uri="/admin/settings"
                )

            if not req.get_param("oauth_verifier", store=params):
                raise HTTPBadRequest("Missing param: oauth_verifier")

            settings = {}

            db_settings = db_session.query(Setting).filter(Setting.key.startswith("twitter_")).all()

            for setting in db_settings:
                settings[setting.key] = setting

            for key in TWITTER_NEEDED_KEYS:
                if key not in settings:
                    resp.append_header("Refresh", "5;url=/admin/settings")

                    return self.render_template(
                        req, resp, "admin/message_gate.html",
                        gate_message=Message(
                            "danger", "Missing setting", "Setting missing: {}".format(key)
                        ),
                        redirect_uri="/admin/settings"
                    )

            for key in TWITTER_OAUTH_KEYS:
                if key not in settings:
                    resp.append_header("Refresh", "5;url=/admin/settings")

                    return self.render_template(
                        req, resp, "admin/message_gate.html",
                        gate_message=Message(
                            "danger", "Missing data", "Data missing: {}".format(key)
                        ),
                        redirect_uri="/admin/settings"
                    )

            twitter = twython.Twython(
                settings["twitter_app_key"].value, settings["twitter_app_secret"].value,
                settings["twitter_oauth_token"].value, settings["twitter_oauth_token_secret"].value
            )

            final_tokens = twitter.get_authorized_tokens(params["oauth_verifier"])

            settings["twitter_oauth_token"].value = final_tokens["oauth_token"]
            settings["twitter_oauth_token_secret"].value = final_tokens["oauth_token_secret"]

            twitter = twython.Twython(
                settings["twitter_app_key"].value, settings["twitter_app_secret"].value,
                settings["twitter_oauth_token"].value, settings["twitter_oauth_token_secret"].value
            )

            user_info = twitter.verify_credentials()

            username = user_info["screen_name"]
            real_name = user_info["name"]

            db_session.add(Setting(key="twitter_username", value=username))

            resp.append_header("Refresh", "5;url=/admin/settings")

            return self.render_template(
                req, resp, "admin/message_gate.html",
                gate_message=Message(
                    "success", "Account linked", "Twitter account linked: {} (@{})".format(
                        real_name, username
                    )
                ),
                redirect_uri="/admin/settings"
            )
