# coding=utf-8
import logging

import twython

from ultros_site.database.schema.setting import Setting
from ultros_site.tasks.__main__ import app
from ultros_site.tasks.base import DatabaseTask

__author__ = "Gareth Coles"

TWITTER_NEEDED_KEYS = [
    "twitter_app_key", "twitter_app_secret",
    "twitter_oauth_token", "twitter_oauth_token_secret"
]


@app.task(base=DatabaseTask, name="send_twitter")
def send_twitter(title: str, url: str):
    with send_twitter.database.session() as session:
        settings = {}

        try:
            db_settings = session.query(Setting).filter(Setting.key.startswith("twitter_")).all()

            for setting in db_settings:
                settings[setting.key] = setting.value
        except Exception as e:
            logging.getLogger("send_twitter").error("Failed to get Twitter credentials: {}".format(e))
        finally:
            session.close()

        for key in TWITTER_NEEDED_KEYS:
            if key not in settings:
                return

        twitter = twython.Twython(
            settings["twitter_app_key"], settings["twitter_app_secret"],
            settings["twitter_oauth_token"], settings["twitter_oauth_token_secret"]
        )

        post = "New post: {}\n{}".format(title, url)

        twitter.update_status(
            enable_dm_commands=False,
            status=post
        )
