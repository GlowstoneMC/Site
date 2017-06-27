# coding=utf-8
from sqlalchemy import func

from ultros_site.base_route import BaseRoute
from ultros_site.database.schema.news_post import NewsPost
from ultros_site.decorators import render_api

__author__ = "Gareth Coles"


class APINewsRoute(BaseRoute):
    route = "/api/v1/news"

    @render_api
    def on_get(self, req, resp):
        page = req.get_param_as_int("page") or 1
        first_index = (page - 1) * 10
        last_index = page * 10

        db_session = req.context["db_session"]
        news_posts = db_session.query(NewsPost).order_by(NewsPost.posted.desc())[first_index:last_index]
        count = db_session.query(func.count(NewsPost.id)).scalar()
        pages = int(count / 10)

        if count % 10:
            pages += 1
        if pages < 1:
            pages = 1

        if page > pages:
            resp.status = "404 Not Found"
            return {
                "error": "Page not found",
                "pages": pages
            }

        return {
            "page": page,
            "pages": pages,
            "posts": [
                {
                    "id": int(post.id),
                    "user": {
                        "id": int(post.user.id),
                        "username": str(post.user.username)
                    },
                    "posted": str(post.posted),
                    "title": str(post.title),
                    "summary": str(post.summary),
                    "markdown": str(post.markdown),
                    "html": str(post.html)
                } for post in news_posts
            ]
        }
