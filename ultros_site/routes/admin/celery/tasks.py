# coding=utf-8
from ultros_site.base_route import BaseRoute
from ultros_site.database.schema.celery_task import CeleryTask
from ultros_site.decorators import check_admin

__author__ = "Gareth Coles"


class IndexRoute(BaseRoute):
    route = "/admin/celery/tasks"

    @check_admin
    def on_get(self, req, resp):
        db_session = req.context["db_session"]
        tasks = db_session.query(CeleryTask).all()

        self.render_template(
            req, resp, "admin/celery_tasks.html",
            tasks=tasks
        )
