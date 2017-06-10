# coding=utf-8
import datetime

from sqlalchemy.orm.exc import NoResultFound

from ultros_site.base_route import BaseRoute
from ultros_site.database.schema.news_post import NewsPost
from ultros_site.decorators import check_admin, add_csrf, check_csrf
from ultros_site.markdown import Markdown
from ultros_site.message import Message
from ultros_site.tasks.notify import notify_post

__author__ = "Gareth Coles"


class CreateNewsRoute(BaseRoute):
    route = "/admin/news/create"

    @check_admin
    @add_csrf
    def on_get(self, req, resp):
        self.render_template(
            req, resp, "admin/news_create.html",
            post=None
        )

    @check_admin
    @check_csrf
    def on_post(self, req, resp):
        params = {}

        if not req.get_param("title", store=params) \
                or not req.get_param("content", store=params):
            resp.append_header("Refresh", "5;url=/admin/news/create")

            return self.render_template(
                req, resp, "admin/message_gate.html",
                gate_message=Message(
                    "danger", "Missing parameters", "Please input both the post title and content."
                ),
                redirect_uri="/admin/news/create"
            )

        markdown = Markdown(params["content"])
        db_session = req.context["db_session"]

        resp.append_header("Refresh", "5;url=/admin/news")

        if not req.get_param("post_id", store=params):
            post = NewsPost(
                user=req.context["user"], posted=datetime.datetime.now(),
                title=params["title"], markdown=markdown.markdown,
                html=markdown.html
            )

            db_session.add(post)
            db_session.commit()

            notify_post(post)

            return self.render_template(
                req, resp, "admin/message_gate.html",
                gate_message=Message(
                    "info", "Post created", "News post created: {}".format(params["title"])
                ),
                redirect_uri="/admin/news"
            )
        else:
            try:
                post = db_session.query(NewsPost).filter_by(id=int(params["post_id"])).one()
            except NoResultFound:
                return self.render_template(
                    req, resp, "admin/message_gate.html",
                    gate_message=Message(
                        "danger", "Error", "No such post: {}".format(params["post_id"])
                    ),
                    redirect_uri="/admin/news"
                )
            else:
                post.title = params["title"]
                post.markdown = markdown.markdown
                post.html = markdown.html

                return self.render_template(
                    req, resp, "admin/message_gate.html",
                    gate_message=Message(
                        "info", "Post edited", "News post edited: {}".format(params["title"])
                    ),
                    redirect_uri="/admin/news"
                )
