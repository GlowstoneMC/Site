# coding=utf-8
import datetime
import logging

from falcon import HTTPSeeOther
from sqlalchemy.orm.exc import NoResultFound

from ultros_site.database.schema.session import Session

__author__ = "Gareth Coles"
log = logging.getLogger("Sessions")


class SessionMiddleware:
    def process_request(self, req, resp):
        if req.path.startswith("/static/"):
            log.debug("Ignoring static file request")
            return

        if req.path.startswith("/api"):
            log.debug("Ignoring API route")
            return

        req.context["user"] = None
        req.context["session"] = None

        cookies = req.cookies

        if "token" not in cookies:
            log.debug("No token present")
            return

        token = cookies["token"]
        db_session = req.context["db_session"]

        try:
            session_obj = db_session.query(Session).filter_by(token=token).one()
        except NoResultFound:
            pass
        else:
            now = datetime.datetime.now()

            if now > session_obj.expires:
                log.debug("Expiring old session")
                db_session.delete(session_obj)
                resp.unset_cookie("token")
            else:
                log.debug("Extending session")
                session_obj.expires = now + datetime.timedelta(days=30)
                req.context["user"] = session_obj.user
                req.context["session"] = session_obj
                age = datetime.timedelta(days=30).seconds

                resp.set_cookie("token", token, max_age=age, secure=False, path="/")

                if session_obj.awaiting_mfa:
                    if req.path not in ["/mfa/challenge", "/logout"]:
                        raise HTTPSeeOther("/mfa/challenge")
