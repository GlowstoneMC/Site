# coding=utf-8
import falcon
import os
import re

from ultros_site.base_sink import BaseSink

__author__ = "Gareth Coles"
BASE_PATH = os.path.abspath("./jd/")


class JavaDocsBaseRoute(BaseSink):
    route = re.compile("^/jd/(?P<project>[^/.]+)$")

    def __call__(self, req, resp, project):
        file_path = os.path.abspath(BASE_PATH + "/" + project)

        index_path = file_path + "/index.html"
        index_path_alternate = file_path + "/index.htm"

        if not file_path.startswith(BASE_PATH):
            raise falcon.HTTPBadRequest(
                description="Invalid request"
            )

        if os.path.isfile(index_path):
            raise falcon.HTTPMovedPermanently(req.uri + "/index.html")
        elif os.path.isfile(index_path_alternate):
            raise falcon.HTTPMovedPermanently(req.uri + "/index.htm")
        else:
            raise falcon.HTTPNotFound()
