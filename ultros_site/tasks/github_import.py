# coding=utf-8
import logging
import requests

from celery import Task
from sqlalchemy.orm.exc import NoResultFound

from ultros_site.database.schema.product_branch import ProductBranch
from ultros_site.database.schema.setting import Setting
from ultros_site.database_manager import DatabaseManager
from ultros_site.tasks.__main__ import app

__author__ = "Momo"

GITHUB_BRANCHES_URL = "https://api.github.com/repos/{}/{}/branches"
GITHUB_NEEDED_KEYS = [
    "github_client_id", "github_client_secret"
]


class ImportTask(Task):
    def __init__(self):
        logging.basicConfig(
            format="%(asctime)s | %(levelname)-8s | %(name)-10s | %(message)s",
            level=logging.INFO
        )

        self.database = DatabaseManager()
        self.database.load_schema()
        self.database.create_engine()


@app.task(base=ImportTask, name="github_import")
def github_import(product_id, gh_owner, gh_project):
    db_session = github_import.database.create_session()
    settings = {}

    try:
        db_settings = db_session.query(Setting).filter(Setting.key.startswith("github_")).all()

        for setting in db_settings:
            settings[setting.key] = setting.value
    except Exception as e:
        logging.getLogger("github_import").error("Failed to get GitHub credentials: {}".format(e))

    for key in GITHUB_NEEDED_KEYS:
        if key not in settings:
            return

    session = requests.session()

    data = session.get(
        GITHUB_BRANCHES_URL.format(gh_owner, gh_project),
        params={
            "client_id": settings["github_client_id"],
            "client_secret": settings["github_client_secret"]
        }
    ).json()

    branches = []

    for branch in data:
        branches.append(branch["name"])
        upsert_branch(db_session, product_id, branch["name"])

    for branch in db_session.query(ProductBranch).filter_by(product_id=product_id).all():
        if branch.name not in branches:
            branch.disabled = True  # TODO: Is this what Momo wanted?


def upsert_branch(session, product_id, branch_name):
    try:
        session.query(ProductBranch).filter_by(product_id=product_id, name=branch_name).one()
    except NoResultFound:
        branch = ProductBranch(product_id=product_id, name=branch_name)
        session.add(branch)
        return True
    return False
