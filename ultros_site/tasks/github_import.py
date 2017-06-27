# coding=utf-8
import logging
import requests

from celery import Task
from sqlalchemy.orm.exc import NoResultFound

from ultros_site.database.schema.product import Product
from ultros_site.database.schema.product_branch import ProductBranch
from ultros_site.database.schema.setting import Setting
from ultros_site.database_manager import DatabaseManager
from ultros_site.tasks.__main__ import app

__author__ = "Momo"

GITHUB_BRANCHES_URL = "https://api.github.com/repos/{}/{}/branches"
GITHUB_REPO_URL = "https://api.github.com/repos/{}/{}"

GITHUB_NEEDED_KEYS = [
    "github_client_id", "github_client_secret",
    "github_oauth_token", "github_username"
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
    with github_import.database.session() as db_session:
        settings = {}

        try:
            db_settings = db_session.query(Setting).filter(Setting.key.startswith("github_")).all()

            for setting in db_settings:
                settings[setting.key] = setting.value
        except Exception as e:
            logging.getLogger("github_import").error("Failed to get GitHub credentials: {}".format(e))

        for key in GITHUB_NEEDED_KEYS:
            if key not in settings:
                logging.getLogger("github_import").warning("Missing settings key: {}".format(key))
                return

        try:
            product = db_session.query(Product).filter(id=product_id).one()
        except NoResultFound:
            logging.getLogger("github_import").warning("No such product: {}".format(product_id))
            return

        session = requests.session()

        data = session.get(
            GITHUB_BRANCHES_URL.format(gh_owner, gh_project),
            params={
                "client_id": settings["github_client_id"],
                "client_secret": settings["github_client_secret"]
            },
            headers={
                "Authorization": "token {}".format(settings["github_oauth_token"])
            }
        ).json()

        logging.getLogger("github_import").info("Received {} branches.".format(len(data)))

        branches = []

        for branch in data:
            name = branch["name"]

            logging.getLogger("github_import").debug("Upserting branch: {}".format(name))

            branches.append(name)
            upsert_branch(db_session, product_id, name)

        for branch in db_session.query(ProductBranch).filter_by(product_id=product_id).all():
            if branch.name not in branches:
                branch.disabled = True

        data = session.get(
            GITHUB_REPO_URL.format(gh_owner, gh_project),
            params={
                "client_id": settings["github_client_id"],
                "client_secret": settings["github_client_secret"]
            },
            headers={
                "Authorization": "token {}".format(settings["github_oauth_token"])
            }
        ).json()

        default_branch = data["default_branch"]

        try:
            db_branch = db_session.query(ProductBranch).filter_by(product_id=product_id, name=default_branch).one()
            product.default_branch = db_branch
        except NoResultFound:
            logging.getLogger("github_import").warning("Failed to find default branch '{}' for product '{}'".format(
                default_branch, product.name
            ))
            return


def upsert_branch(session, product_id, branch_name):
    try:
        session.query(ProductBranch).filter_by(product_id=product_id, name=branch_name).one()
    except NoResultFound:
        branch = ProductBranch(product_id=product_id, name=branch_name)
        session.add(branch)
    else:
        return False

    try:
        product = session.query(Product).filter_by(id=product_id).one()
    except NoResultFound:
        return None
    else:
        product.branches.append(branch)

    return True
