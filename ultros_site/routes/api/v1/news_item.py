# coding=utf-8
import re

from sqlalchemy.orm.exc import NoResultFound

from ultros_site.base_sink import BaseSink
from ultros_site.database.schema.news_post import NewsPost
from ultros_site.decorators import render_api

__author__ = "Gareth Coles"


class APINewsRoute(BaseSink):
    route = re.compile(r"/api/v1/news/(?P<index>\d+)")

    @render_api
    def __call__(self, req, resp, index):
        db_session = req.context["db_session"]

        try:
            post = db_session.query(NewsPost).filter_by(published=True, id=int(index)).one()
        except NoResultFound:
            resp.status = "404 Not Found"

            return {
                "error": "Post not found",
                "id": index
            }

        return {
            "id": int(post.id),
            "user": {
                "id": int(post.user.id),
                "username": str(post.user.username)
            },
            "posted": str(post.posted),
            "title": str(post.title),
            "summary": str(post.summary),
            "markdown": str(post.markdown),
            "html": str(post.html),
            "comment_url": str(post.comment_url) if post.comment_url else None
        }
