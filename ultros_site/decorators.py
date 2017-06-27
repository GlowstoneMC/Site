# coding=utf-8
import logging
import secrets

from falcon import HTTPBadRequest, HTTPForbidden

__author__ = "Gareth Coles"
log = logging.getLogger("Decorators")


def check_csrf(func):
    def inner(self, req, *args, **kwargs):
        cookies = []
        cookies_string = req.get_header("Cookie")

        for cookie in cookies_string.split("; "):
            left, right = cookie.split("=", 1)

            if left == "_csrf":
                cookies.append(right)

        if not cookies:
            log.debug("Missing CSRF token from cookies")
            raise HTTPBadRequest(
                "Missing CSRF token",
                "The request is missing a CSRF token."
            )

        post_token = req.get_param("_csrf")

        if post_token is None:
            log.debug("Missing CSRF token from form")
            raise HTTPBadRequest(
                "Missing CSRF token",
                "The request is missing a CSRF token."
            )

        if post_token not in cookies:
            log.debug("CSRF tokens don't match")
            log.debug("Given: {}".format(post_token))
            log.debug("Expected: {}".format(" / ".join(cookies)))
            log.debug("All cookies: {}".format(cookies_string))

            raise HTTPBadRequest(
                "Missing CSRF token",
                "The CSRF tokens do not match."
            )

        return func(self, req, *args, **kwargs)
    return inner


def add_csrf(func):
    def inner(self, req, resp, *args, **kwargs):
        token = secrets.token_urlsafe(32)

        resp.set_cookie("_csrf", token, secure=False, http_only=False)
        resp.csrf = token

        return func(self, req, resp, *args, **kwargs)
    return inner


def check_admin(func):
    def inner(self, req, resp, *args, **kwargs):
        user = req.context["user"]

        if user and user.admin:
            return func(self, req, resp, *args, **kwargs)

        raise HTTPForbidden()
    return inner


def check_api(func):
    def inner(self, req, resp, *args, **kwargs):
        user = req.context["user"]

        if user and user.api_enabled:
            return func(self, req, resp, *args, **kwargs)

        resp.status = "403 Bad Request"
        resp.content_type = "text"
        resp.body = "API access is disabled for your account"
    return inner
