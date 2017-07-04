# coding=utf-8
import logging

import requests

from ultros_site.database.schema.setting import Setting
from ultros_site.tasks.__main__ import app
from ultros_site.tasks.base import DatabaseTask

__author__ = "Gareth Coles"


@app.task(base=DatabaseTask, name="send_discord")
def send_discord(embed: None):
    with send_discord.database.session() as session:
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
        session.post(hook_url, json={
            "embeds": embeds
        })
