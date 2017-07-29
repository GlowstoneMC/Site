# coding=utf-8
import logging
from operator import itemgetter

import requests

from sqlalchemy.orm.exc import NoResultFound

from ultros_site.database.schema.news_post import NewsPost
from ultros_site.database.schema.setting import Setting
from ultros_site.tasks.__main__ import app
from ultros_site.tasks.base import DatabaseTask

__author__ = "Gareth Coles"

NODEBB_URL = "https://forums.glowstone.net/api/category/12/announcements"
NODEBB_LOCATION = "https://forums.glowstone.net/topic/{}/9999"

NODEBB_NEEDED_KEYS = [
    "nodebb_api_key", "nodebb_base_url",
    "nodebb_category_id", "nodebb_default_user_id"
]

NODEBB_WRITE_API_PATH = "/api/v1"
NODEBB_READ_API_PATH = "/api"

NODEBB_READ_EMAIL = "%s/user/email/{}" % NODEBB_READ_API_PATH
NODEBB_WRITE_POST = "%s/topics" % NODEBB_WRITE_API_PATH


@app.task(base=DatabaseTask, name="link_comments")
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

        found = False

        for topic in topics:
            if topic["title"] == post.title:
                found = True

                location = NODEBB_LOCATION.format(topic["slug"])

                if not session.query(NewsPost).filter_by(comment_url=location).count():
                    post.comment_url = location
                    break

        if not found:
            post.comment_url = None
            return

        logging.getLogger("link_comments").warning(
            "Unable to find an unlinked topic for post: {} ({})".format(post.title, post.id)
        )


@app.task(base=DatabaseTask, name="send_nodebb")
def send_nodebb(title, url, markdown, username, email, post_id):
    with send_nodebb.database.session() as session:
        settings = {}

        # Load up all NodeBB settings

        try:
            for setting in session.query(Setting).filter(Setting.key.like("nodebb_%")).all():
                settings[setting.key] = setting.value
        except Exception as e:
            logging.getLogger("send_nodebb").error("Failed to get NodeBB settings: {}".format(e))
            return
        finally:
            session.close()

        for key in NODEBB_NEEDED_KEYS:
            if key not in settings:
                return  # Not enough settings available

        nodebb_url = settings["nodebb_base_url"] + "{}"

        # Attempt to find a user object by email

        try:
            resp = requests.get(nodebb_url.format(NODEBB_READ_EMAIL.format(email)))
        except Exception as e:
            logging.getLogger("send_nodebb").warning("Failed to find a user for {}: {}".format(email, e))
            uid = settings["nodebb_default_user_id"]
            title = "{} (by {})".format(title, username)
        else:
            data = resp.json()
            uid = data["uid"]

        markdown = "{}\n\n*This post was mirrored from [the site]({}).*".format(markdown, url)

        try:
            requests.post(
                nodebb_url.format(NODEBB_WRITE_POST), data={
                    "_uid": uid,
                    "cid": settings["nodebb_category_id"],
                    "title": title,
                    "content": markdown
                },
                headers={
                    "Authorization": "Bearer {}".format(settings["nodebb_api_key"])
                }
            )

            app.send_task(
                "link_comments",
                args=[post_id]
            )
        except Exception as e:
            logging.getLogger("send_nodebb").error("Unable to create post: {}".format(e))
