# coding=utf-8
import json

import requests
from celery import Task

from ultros_site.tasks.__main__ import app

__author__ = "Momo"


class GithubImportTask(Task):
    def __init__(self):
        pass


@app.task(base=GithubImportTask, name="github_import")
def github_import(callback, product, existing_branches, gh_owner, gh_project, gh_user, gh_token, *args, **kwargs):
    endpoint = str.format("https://{}:{}@api.github.com/repos/{}/{}/branches", gh_user, gh_token, gh_owner, gh_project)
    print("Sending at ", endpoint)
    session = requests.session()
    data = json.loads(session.get(endpoint).text)
    # todo: actually do something with the data (importing)
    for b in data:
        b_name = b["name"]
        print(b_name)
    callback(product, data)
    return True
