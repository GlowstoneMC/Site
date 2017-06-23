# coding=utf-8
import re

from sqlalchemy.orm.exc import NoResultFound

from ultros_site.base_sink import BaseSink
from ultros_site.database.schema.user import User
from ultros_site.decorators import check_csrf, check_admin
from ultros_site.message import Message

__author__ = "Gareth Coles"


class DisableUserAPIRoute(BaseSink):
    route = re.compile("/admin/users/enable_api/(?P<user_id>.*)")

    @check_admin
    @check_csrf
    def __call__(self, req, resp, user_id):
        user_id = int(user_id)
        db_session = req.context["db_session"]

        try:
            db_user = db_session.query(User).filter_by(id=user_id).one()
        except NoResultFound:
            resp.append_header("Refresh", "5;url=/admin/users")

            return self.render_template(
                req, resp, "admin/message_gate.html",
                gate_message=Message(
                    "danger", "Unknown user", "User with ID <code>{}</code> not found.".format(user_id)
                ),
                redirect_uri="/admin/users"
            )
        else:
            resp.append_header("Refresh", "5;url=/admin/users")

            if not db_user.api_enabled:
                db_user.api_enabled = True

                return self.render_template(
                    req, resp, "admin/message_gate.html",
                    gate_message=Message(
                        "success", "API access granted", "You have granted API access for {}".format(db_user.username)
                    ),
                    redirect_uri="/admin/users"
                )
            else:
                return self.render_template(
                    req, resp, "admin/message_gate.html",
                    gate_message=Message(
                        "warning", "MFA already disabled", "That user already has API access."
                    ),
                    redirect_uri="/admin/users"
                )
