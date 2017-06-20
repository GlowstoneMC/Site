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

NODEBB_NEEDED_KEYS = [
    "nodebb_api_key", "nodebb_base_url",
    "nodebb_category_id", "nodebb_default_user_id"
]

NODEBB_WRITE_API_PATH = "/api/v1"
NODEBB_READ_API_PATH = "/api"

NODEBB_READ_EMAIL = "%s/user/email/{}" % NODEBB_READ_API_PATH
NODEBB_WRITE_POST = "%s/topics"


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

    # NodeBB

    app.send_task(
        "send_nodebb",
        args=[post.title, post_url, post.markdown, post.user.username, post.user.email]
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


@app.task(base=NotifyTask, name="send_nodebb")
def send_nodebb(title, url, markdown, username, email):
    session = send_nodebb.database.create_session()
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

    # Attempt to find a user object by email

    try:
        resp = requests.get(NODEBB_READ_EMAIL.format(email))
    except Exception as e:
        logging.getLogger("send_nodebb").warning("Failed to find a user for {}: {}".format(email, e))
        uid = settings["nodebb_default_user_id"]
        title = "{} (by {})".format(title, username)
    else:
        data = resp.json()
        uid = data["uid"]

    markdown = "{}\n\n*This post was mirrored from [the site]({}).*".format(markdown, url)

    try:
        resp = requests.post(
            NODEBB_WRITE_POST, data={
                "_uid": uid,
                "cid": settings["nodebb_category_id"],
                "title": title,
                "content": markdown
            },
            headers={
                "Authorization": "Bearer {}".format(settings["nodebb_api_key"])
            }
        )
    except Exception as e:
        logging.getLogger("send_nodebb").error("Unable to create post: {}".format(e))
