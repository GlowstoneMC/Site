# coding=utf-8
import falcon
import os
import re

from mimetypes import guess_type

from ultros_site.base_sink import BaseSink

__author__ = "Gareth Coles"
BASE_PATH = os.path.abspath("./jd/")


class JavaDocsRoute(BaseSink):
    route = re.compile("/jd/(?P<project>[^/]+)/(?P<filename>.*)")

    def __call__(self, req, resp, project, filename):
        file_path = os.path.abspath(BASE_PATH + "/" + project + "/" + filename)
        base_path = os.path.dirname(file_path)
        index_path = os.path.abspath(base_path + "/index.html")
        index_path_alternate = os.path.abspath(base_path + "/index.htm")

        if not file_path.startswith(BASE_PATH):
            raise falcon.HTTPBadRequest(
                description="Invalid request"
            )

        if not os.path.isfile(file_path):
            if os.path.isfile(index_path):
                file_path = index_path
            elif os.path.isfile(index_path_alternate):
                file_path = index_path_alternate
            else:
                raise falcon.HTTPNotFound()

        content_type = guess_type(file_path)[0]

        if content_type:
            resp.content_type = content_type

        fh = open(file_path, "rb")

        resp.stream = fh
        resp.stream_len = os.path.getsize(file_path)

        resp.status = falcon.HTTP_200
