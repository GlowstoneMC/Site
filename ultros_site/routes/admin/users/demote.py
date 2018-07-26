# coding=utf-8
import re

from sqlalchemy.orm.exc import NoResultFound

from ultros_site.base_sink import BaseSink
from ultros_site.database.schema.user import User
from ultros_site.decorators import check_csrf, check_admin
from ultros_site.message import Message

__author__ = "Gareth Coles"


class DemoteUserRoute(BaseSink):
    route = re.compile("/admin/users/demote/(?P<user_id>.*)")

    @check_admin
    @check_csrf
    def __call__(self, req, resp, user_id):
        user_id = int(user_id)
        current_user = req.context["user"]

        if user_id == current_user.id:
            # Don't demote yourself!
            resp.append_header("Refresh", "5;url=/admin/users")

            return self.render_template(
                req, resp, "admin/message_gate.html",
                gate_message=Message(
                    "danger", "Error", "You may not demote yourself."
                ),
                redirect_uri="/admin/users"
            )

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

            if db_user.username == self.manager.database.config.admin_username:
                return self.render_template(
                    req, resp, "admin/message_gate.html",
                    gate_message=Message(
                        "danger", "Error", "You may not demote the configured default admin account."
                    ),
                    redirect_uri="/admin/users"
                )

            if db_user.admin:
                db_user.admin = False

                return self.render_template(
                    req, resp, "admin/message_gate.html",
                    gate_message=Message(
                        "success", "User demoted", "That user has been demoted."
                    ),
                    redirect_uri="/admin/users"
                )
            else:
                return self.render_template(
                    req, resp, "admin/message_gate.html",
                    gate_message=Message(
                        "danger", "Error", "That user is not an admin!"
                    ),
                    redirect_uri="/admin/users"
                )
