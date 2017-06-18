# coding=utf-8
import logging
import requests
import twython

from celery import Task

from ultros_site.database.schema.news_post import NewsPost
from ultros_site.database.schema.setting import Setting
from ultros_site.database_manager import DatabaseManager
from ultros_site.tasks.__main__ import app

__author__ = "Gareth Coles"

TWITTER_NEEDED_KEYS = [
    "twitter_app_key", "twitter_app_secret",
    "twitter_oauth_token", "twitter_oauth_token_secret"
]


class NotifyTask(Task):
    def __init__(self):
        logging.basicConfig(
            format="%(asctime)s | %(levelname)-8s | %(name)-10s | %(message)s",
            level=logging.INFO
        )

        self.database = DatabaseManager()
        self.database.load_schema()
        self.database.create_engine()


def notify_post(post: NewsPost):
    post_url = "https://glowstone.net/news/{}".format(post.id)

    # Discord

    md = post.markdown.replace("\r", "")

    if "\n\n" in md:
        md = md.split("\n\n")[0].replace("\n", "")

    md += "\n\n"
    md += "[Click here for more]({})".format(post_url)

    discord_embed = {
        "title": post.title,
        "description": md,
        "url": post_url,
        "author": {
            "name": post.user.username,
            "url": "https://glowstone.net/"
        }
    }

    app.send_task(
        "send_discord",
        args=[discord_embed]
    )

    # Twitter

    app.send_task(
        "send_twitter",
        args=[post.title, post_url]
    )


@app.task(base=NotifyTask, name="send_twitter")
def send_twitter(title: str, url: str):
    session = send_discord.database.create_session()
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
            logging.getLogger("send_twitter").error("Missing setting: {}".format(key))
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


@app.task(base=NotifyTask, name="send_discord")
def send_discord(embed: None):
    session = send_discord.database.create_session()

    try:
        setting = session.query(Setting).filter_by(key="discord_webhook_url").one()
        hook_url = setting.value
    except Exception as e:
        logging.getLogger("send_discord").error("Failed to get hook URL: {}".format(e))
        return
    finally:
        session.close()

    if embed is None:
        embeds = []
    else:
        embeds = [embed]

    session = requests.session()
    return session.post(hook_url, json={
        "embeds": embeds
    })
