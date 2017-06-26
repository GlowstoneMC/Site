# coding=utf-8

__author__ = "Gareth Coles"


class ErrorPageMiddleware:
    def __init__(self, routes_manager):
        self.routes_manager = routes_manager

    def process_response(self, req, resp, resource, req_succeeded):
        if req_succeeded:
            return

        if req.path.startswith("/api"):
            return

        if " " in resp.status:
            status_code, error_description = resp.status.split(" ", 1)
            status_code = int(status_code)
        else:
            status_code = int(resp.status)
            error_description = "Unknown Error"

        if status_code < 400:
            return

        try:
            resp.content_type, resp.body = self.routes_manager.render_template(
                "errors/error_{}.html".format(status_code),
                _context=req.context,
                code=status_code,
                req=req,
                resp=resp
            )

            resp.data = None
            resp.stream = None
        except Exception:
            pass
        else:
            return

        try:
            resp.content_type, resp.body = self.routes_manager.render_template(
                "errors/error_generic.html",
                _context=req.context,
                code=status_code,
                error_description=error_description,
                req=req,
                resp=resp
            )

            resp.data = None
            resp.stream = None
        except Exception as e:
            resp.content_type = "text/plain"
            resp.body = "Failed to render page for HTTP {}: {}".format(
                resp.status, e
            )

            resp.data = None
            resp.stream = None
