# coding=utf-8
import logging

from sqlalchemy.orm.exc import NoResultFound

from ultros_site.database.schema.api_key import APIKey

__author__ = "Gareth Coles"
log = logging.getLogger("API")


class APIMiddleware:
    def process_request(self, req, resp):
        if not req.path.startswith("/api"):
            log.debug("Ignoring non-API route")
            return

        req.context["user"] = None

        params = {}
        api_key = None

        if not req.get_param("api_key", store=params):
            auth_header = req.get_header("Authorization")

            if auth_header:
                api_key = auth_header
        else:
            api_key = params["api_key"]

        if not api_key:
            return  # Not authorized

        db_session = req.context["db_session"]

        try:
            user = db_session.query(APIKey).filter_by(key=api_key).one()
        except NoResultFound:
            return  # Not authorized
        else:
            req.context["user"] = user
