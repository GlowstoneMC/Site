# coding=utf-8
import json
import logging
import pprint

from ultros_site.base_route import BaseRoute
from ultros_site.decorators import render_api

__author__ = "Gareth Coles"


class APIBuildsNotifyGitHubRoute(BaseRoute):
    route = "/api/v1/builds/notify/github"

    @render_api
    def on_post(self, req, resp):
        logger = logging.getLogger("GitHub")
        data = json.load(req.bounded_stream)

        logger.info("\n{}\n".format(pprint.pformat(data)))

        return {}
