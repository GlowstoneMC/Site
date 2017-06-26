# coding=utf-8

from sqlalchemy.orm.exc import NoResultFound

from ultros_site.base_route import BaseRoute
from ultros_site.database.schema.setting import Setting
from ultros_site.decorators import check_admin, add_csrf, check_csrf
from ultros_site.message import Message

__author__ = "Gareth Coles"


class SettingsRoute(BaseRoute):
    route = "/admin/settings"

    @check_admin
    @add_csrf
    def on_get(self, req, resp):
        settings = {}
        db_session = req.context["db_session"]

        for setting in db_session.query(Setting).all():
            settings[setting.key] = setting.value

        self.render_template(
            req, resp, "admin/settings.html",
            settings=settings,
            post=None
        )

    @check_admin
    @check_csrf
    def on_post(self, req, resp):
        params = {}
        db_session = req.context["db_session"]

        req.get_param("twitter_app_key", store=params)
        req.get_param("twitter_app_secret", store=params)
        req.get_param("discord_webhook_url", store=params)

        req.get_param("nodebb_api_key", store=params)
        req.get_param("nodebb_base_url", store=params)
        req.get_param("nodebb_category_id", store=params)
        req.get_param("nodebb_default_user_id", store=params)

        req.get_param("github_client_id", store=params)
        req.get_param("github_client_secret", store=params)

        if "nodebb_base_url" in params and params["nodebb_base_url"][-1] == "/":
            params["nodebb_base_url"] = params["nodebb_base_url"][:-1]

        for key, value in params.items():
            if not value:
                continue

            try:
                setting = db_session.query(Setting).filter_by(key=key).one()
            except NoResultFound:
                setting = Setting(key=key, value=value)
                db_session.add(setting)
            else:
                if not value:
                    db_session.delete(setting)
                else:
                    setting.value = value

        resp.append_header("Refresh", "5;url=/admin/settings")

        return self.render_template(
            req, resp, "admin/message_gate.html",
            gate_message=Message(
                "info", "Settings updated", "Application settings have been updated."
            ),
            redirect_uri="/admin/settings"
        )
