# coding=utf-8

from ultros_site.database.schema.news_post import NewsPost
from ultros_site.tasks.__main__ import app

__author__ = "Gareth Coles"


def notify_post(post: NewsPost):
    post_url = "https://beta.glowstone.net/news/{}".format(post.id)

    # Discord

    md = post.summary

    md += "\n\n"
    md += "[Click here for more]({})".format(post_url)

    discord_embed = {
        "title": post.title,
        "description": md,
        "url": post_url,
        "author": {
            "name": post.user.username,
            "url": "https://beta.glowstone.net/"
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
        args=[post.title, post_url, post.markdown, post.user.username, post.user.email, post.id]
    )
