# coding=utf-8
import logging
from operator import itemgetter

import requests

from celery import Task
from sqlalchemy.orm.exc import NoResultFound

from ultros_site.database.schema.news_post import NewsPost
from ultros_site.database_manager import DatabaseManager
from ultros_site.tasks.__main__ import app

__author__ = "Gareth Coles"

NODEBB_URL = "https://forums.glowstone.net/api/category/12/announcements"
NODEBB_LOCATION = "https://forums.glowstone.net/topic/{}/9999"


class NotifyTask(Task):
    def __init__(self):
        logging.basicConfig(
            format="%(asctime)s | %(levelname)-8s | %(name)-10s | %(message)s",
            level=logging.WARNING
        )

        self.database = DatabaseManager()
        self.database.load_schema()
        self.database.create_engine()


@app.task(base=NotifyTask, name="link_comments")
def link_comments(post_id: int):
    with link_comments.database.session() as session:
        try:
            post = session.query(NewsPost).filter_by(id=post_id).one()
        except NoResultFound:
            return

        http = requests.session()
        resp = http.get(NODEBB_URL).json()

        if "topics" not in resp:
            return

        topics = sorted(resp["topics"], key=itemgetter("tid"))

        for topic in topics:
            if topic["title"] == post.title:
                location = NODEBB_LOCATION.format(topic["slug"])

                if not session.query(NewsPost).filter_by(comment_url=location).count():
                    post.comment_url = location
                    return

        logging.getLogger("link_comments").warning(
            "Unable to find an unlinked topic for post: {} ({})".format(post.title, post.id)
        )
