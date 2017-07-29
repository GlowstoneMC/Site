# coding=utf-8
import re

from falcon.errors import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound

from ultros_site.base_sink import BaseSink
from ultros_site.database.schema.news_post import NewsPost
from ultros_site.markdown import Markdown

__author__ = "Gareth Coles"


class NewsViewRoute(BaseSink):
    route = re.compile(r"/news/(?P<post_id>\d+)")

    def __call__(self, req, resp, post_id):
        db_session = req.context["db_session"]
        news_posts = db_session.query(NewsPost).filter_by(published=True).order_by(NewsPost.posted.desc())[0:3]

        try:
            news_post = db_session.query(NewsPost).filter_by(id=post_id, published=True).one()
        except NoResultFound:
            raise HTTPNotFound()

        if news_post.summary is None:
            markdown = Markdown(news_post.markdown)
            news_post.summary = markdown.summary

        self.render_template(
            req, resp, "news_view.html",
            post=news_post,
            news_posts=news_posts
        )
