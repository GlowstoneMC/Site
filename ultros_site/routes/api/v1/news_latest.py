# coding=utf-8
from ultros_site.base_route import BaseRoute
from ultros_site.database.schema.news_post import NewsPost
from ultros_site.decorators import render_api

__author__ = "Gareth Coles"


class APINewsRoute(BaseRoute):
    route = "/api/v1/news/latest"

    @render_api
    def on_get(self, req, resp):

        db_session = req.context["db_session"]
        post = db_session.query(NewsPost).filter_by(published=True).order_by(
            NewsPost.posted.desc()
        ).first()

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
