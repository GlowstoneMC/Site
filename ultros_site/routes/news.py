# coding=utf-8
from sqlalchemy import func

from ultros_site.base_route import BaseRoute
from ultros_site.database.schema.news_post import NewsPost

__author__ = "Gareth Coles"


class NewsRoute(BaseRoute):
    route = "/news"

    def on_get(self, req, resp):
        page = req.get_param_as_int("page") or 1
        first_index = (page - 1) * 10
        last_index = page * 10

        db_session = req.context["db_session"]
        all_posts = db_session.query(NewsPost).filter_by(published=True).order_by(
            NewsPost.posted.desc()
        )
        news_posts = all_posts[first_index:last_index]
        latest_news_posts = all_posts[0:3]
        count = db_session.query(func.count(NewsPost.id)).scalar()
        pages = int(count / 10)

        if count % 10:
            pages += 1
        if pages < 1:
            pages = 1

        self.render_template(
            req, resp, "news.html",
            page=page,
            pages=pages,
            news_posts=news_posts,
            latest_news=latest_news_posts
        )
