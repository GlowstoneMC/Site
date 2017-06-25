# coding=utf-8
import re
import secrets
from urllib.parse import quote_plus

import twython

from falcon import HTTPBadRequest, HTTPFound
from requests import session
from sqlalchemy.orm.exc import NoResultFound

from ultros_site.base_sink import BaseSink
from ultros_site.database.schema.setting import Setting
from ultros_site.decorators import check_admin, check_csrf
from ultros_site.message import Message

__author__ = "Gareth Coles"
SERVICES = ["twitter", "github"]
ACTIONS = ["link", "unlink", "auth"]

TWITTER_NEEDED_KEYS = ["twitter_app_key", "twitter_app_secret"]
TWITTER_OAUTH_KEYS = ["twitter_oauth_token", "twitter_oauth_token_secret"]

GITHUB_NEEDED_KEYS = ["github_client_id", "github_client_secret"]
GITHUB_OAUTH_KEYS = ["github_oauth_token", "github_oauth_state"]

GITHUB_REDIRECT_URL = "https://github.com/login/oauth/authorize?{}"
GITHUB_REDIRECT_PARAMS = {
    "allow_signup": "false",
    "scope": "repo",
    "redirect_uri": "https://beta.glowstone.net/admin/oauth/github/auth",
    "client_id": None,
    "state": None
}

GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"


class SettingsRoute(BaseSink):
    route = re.compile("/admin/oauth/(?P<service>[^/]+)/(?P<action>[^/]+)")

    @check_admin
    def __call__(self, req, resp, service, action):
        if service not in SERVICES:
            raise HTTPBadRequest("Unknown service: {}".format(service))

        if action not in ACTIONS:
            raise HTTPBadRequest("Unknown action: {}".format(action))

        return getattr(self, "do_{}_{}".format(action, service))(req, resp)

    def do_link_github(self, req, resp):
        db_session = req.context["db_session"]

        try:
            db_session.query(Setting).filter_by(key="github_username").one()
        except NoResultFound:
            pass  # Good!
        else:
            resp.append_header("Refresh", "5;url=/admin/settings")

            return self.render_template(
                req, resp, "admin/message_gate.html",
                gate_message=Message(
                    "warning", "Already linked", "A GitHub account is already linked - please unlink it first."
                ),
                redirect_uri="/admin/settings"
            )

        settings = {}

        db_settings = db_session.query(Setting).filter(Setting.key.startswith("github_")).all()

        for setting in db_settings:
            if setting.key in GITHUB_OAUTH_KEYS or setting.key == "github_username":
                db_session.delete(setting)
                continue

            settings[setting.key] = setting.value

        db_session.commit()

        for key in GITHUB_NEEDED_KEYS:
            if key not in settings:
                resp.append_header("Refresh", "5;url=/admin/settings")

                return self.render_template(
                    req, resp, "admin/message_gate.html",
                    gate_message=Message(
                        "danger", "Missing setting", "Setting missing: {}".format(key)
                    ),
                    redirect_uri="/admin/settings"
                )

        state = Setting(key="github_oauth_state", value=secrets.token_urlsafe(32))

        db_session.add(state)
        db_session.add(Setting(key="github_oauth_token", value=""))

        db_session.commit()

        params = GITHUB_REDIRECT_PARAMS.copy()
        params["client_id"] = settings["github_client_id"]
        params["state"] = state.value

        params_list = []

        for param, value in params.items():
            params_list.append(
                "{}={}".format(param, quote_plus(value))
            )

        raise HTTPFound(
            GITHUB_REDIRECT_URL.format("&".join(params_list))
        )

    @check_csrf
    def do_unlink_github(self, req, resp):
        db_session = req.context["db_session"]

        try:
            db_session.query(Setting).filter_by(key="github_username").one()
        except NoResultFound:
            resp.append_header("Refresh", "5;url=/admin/settings")

            return self.render_template(
                req, resp, "admin/message_gate.html",
                gate_message=Message(
                    "warning", "No account linked", "No GitHub account is currently linked."
                ),
                redirect_uri="/admin/settings"
            )
        else:
            db_settings = db_session.query(Setting).filter(Setting.key.startswith("github_")).all()

            for setting in db_settings:
                if setting.key in GITHUB_OAUTH_KEYS or setting.key == "github_username":
                    db_session.delete(setting)
                    continue

            db_session.commit()

            resp.append_header("Refresh", "5;url=/admin/settings")

            return self.render_template(
                req, resp, "admin/message_gate.html",
                gate_message=Message(
                    "success", "Account unlinked", "The GitHub account has been unlinked."
                ),
                redirect_uri="/admin/settings"
            )

    def do_auth_github(self, req, resp):
        db_session = req.context["db_session"]
        params = {}

        try:
            db_session.query(Setting).filter_by(key="github_username").one()
        except NoResultFound:
            pass  # Good!
        else:
            resp.append_header("Refresh", "5;url=/admin/settings")

            return self.render_template(
                req, resp, "admin/message_gate.html",
                gate_message=Message(
                    "warning", "Already linked", "A GitHub account is already linked - please unlink it first."
                ),
                redirect_uri="/admin/settings"
            )

        if not req.get_param("code", store=params):
            raise HTTPBadRequest("Missing param: code")

        if not req.get_param("state", store=params):
            raise HTTPBadRequest("Missing param: state")

        settings = {}

        db_settings = db_session.query(Setting).filter(Setting.key.startswith("github_")).all()

        for setting in db_settings:
            settings[setting.key] = setting

        for key in GITHUB_NEEDED_KEYS:
            if key not in settings:
                resp.append_header("Refresh", "5;url=/admin/settings")

                return self.render_template(
                    req, resp, "admin/message_gate.html",
                    gate_message=Message(
                        "danger", "Missing setting", "Setting missing: {}".format(key)
                    ),
                    redirect_uri="/admin/settings"
                )

        for key in GITHUB_OAUTH_KEYS:
            if key not in settings:
                resp.append_header("Refresh", "5;url=/admin/settings")

                return self.render_template(
                    req, resp, "admin/message_gate.html",
                    gate_message=Message(
                        "danger", "Missing data", "Data missing: {}".format(key)
                    ),
                    redirect_uri="/admin/settings"
                )

        if not params["state"] == settings["github_oauth_state"]:
            raise HTTPBadRequest("Invalid state")

        http = session()

        params = {
            "client_id": settings["github_client_id"],
            "client_secret": settings["github_client_secret"],
            "code": params["code"],
            "state": settings["github_oauth_state"]
        }

        response = http.post(GITHUB_TOKEN_URL, data=params, headers={"Accept": "application/json"}).json()

        oauth_token = db_session.query(Setting).filter_by(key="github_oauth_token").one()
        oauth_token.value = response["access_token"]

        user = http.get(GITHUB_USER_URL, headers={"Authorization", "token {}".format(oauth_token.value)}).json()

        db_session.add(Setting(key="github_username", value=user["login"]))

        resp.append_header("Refresh", "5;url=/admin/settings")

        return self.render_template(
            req, resp, "admin/message_gate.html",
            gate_message=Message(
                "success", "Account linked", "GitHub account linked: {}".format(
                    user["login"]
                )
            ),
            redirect_uri="/admin/settings"
        )

    def do_link_twitter(self, req, resp):
        db_session = req.context["db_session"]

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
    def do_unlink_twitter(self, req, resp):
        db_session = req.context["db_session"]

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
                    "success", "Account unlinked", "The Twitter account has been unlinked."
                ),
                redirect_uri="/admin/settings"
            )

    def do_auth_twitter(self, req, resp):
        db_session = req.context["db_session"]
        params = {}

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
