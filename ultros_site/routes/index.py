# coding=utf-8
from ultros_site.base_route import BaseRoute
from ultros_site.database.schema.news_post import NewsPost

__author__ = "Gareth Coles"


class IndexRoute(BaseRoute):
    route = "/"

    def on_get(self, req, resp):
        db_session = req.context["db_session"]
        news_posts = db_session.query(NewsPost).order_by(NewsPost.posted.desc())[0:3]

        self.render_template(
            req, resp, "index.html",
            news_posts=news_posts
        )
