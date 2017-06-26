# coding=utf-8
from ultros_site.tasks.__main__ import app as celery
from ultros_site.base_route import BaseRoute
from ultros_site.decorators import check_admin

__author__ = "Gareth Coles"


class IndexRoute(BaseRoute):
    route = "/admin/celery/workers"

    @check_admin
    def on_get(self, req, resp):
        i = celery.control.inspect()

        stats = i.stats()
        scheduled = i.scheduled()
        active = i.active()
        reserved = i.reserved()
        registered = i.registered()

        self.render_template(
            req, resp, "admin/celery_workers.html",
            stats=stats,

            scheduled=scheduled,
            active=active,
            reserved=reserved,
            registered=registered
        )
