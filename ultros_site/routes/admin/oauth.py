# coding=utf-8
import re
from pprint import pformat

import twython

from falcon import HTTPBadRequest, HTTPFound
from requests_oauthlib import OAuth2Session
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
GITHUB_OAUTH_KEYS = ["github_oauth_token"]

GITHUB_REDIRECT_URL = "https://github.com/login/oauth/authorize"
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

        db_session.add(Setting(key="github_oauth_token", value=""))
        db_session.commit()

        github = OAuth2Session(settings["github_client_id"])
        url, _ = github.authorization_url(GITHUB_REDIRECT_URL)

        raise HTTPFound(url)

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

        github = OAuth2Session(settings["github_client_id"])
        response = github.fetch_token(
            GITHUB_TOKEN_URL, client_secret=settings["github_client_secret"],
            code=params["code"]
        )

        if "access_token" not in response:
            resp.append_header("Refresh", "15;url=/admin/settings")

            return self.render_template(
                req, resp, "admin/message_gate.html",
                gate_message=Message(
                    "success", "Bad data", "Response: <pre>{}</pre>".format(pformat(response))
                ),
                redirect_uri="/admin/settings"
            )

        oauth_token = db_session.query(Setting).filter_by(key="github_oauth_token").one()
        oauth_token.value = response["access_token"]

        user = github.get(GITHUB_USER_URL).json()

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
