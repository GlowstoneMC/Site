# coding=utf-8
import json

from ultros_site.base_route import BaseRoute
from ultros_site.decorators import render_api, check_admin, check_api
from ultros_site.tasks.__main__ import app as celery

__author__ = "Gareth Coles"


class APIBuildsNotifyGitHubRoute(BaseRoute):
    route = "/api/v1/builds/notify/github"

    @check_api
    @check_admin
    @render_api
    def on_post(self, req, resp):
        if req.get_header("content-type") != "application/json":
            resp.status = "400 Bad Request"
            resp.content_type = "text"
            resp.body = "Data was not of type 'application/json'"
            return

        event_type = req.get_header("X-GitHub-Event")
        data = json.load(req.bounded_stream)

        state = data["state"]
        project = data["name"]
        context = data["context"]
        branches = [b["name"] for b in data["branches"]]

        if event_type != "status":
            return

        if not project.startswith("GlowstoneMC/"):
            return
        if context != "ci/circleci: build-deploy":
            return
        if state != "success":
            return
        if "dev" not in branches:
            return

        celery.send_task(
            "download_javadocs",
            args=[project]
        )

        return
