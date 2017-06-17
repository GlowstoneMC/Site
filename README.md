Glowstone Site
==============

This is the code for the new downloads site for Glowstone, and potentially for a full site replacement
later. Based on the code for [the Ultros site](https://github.com/UltrosBot/Ultros-site).

This project uses the Ace editor in the admin interface. The license for Ace
can be found in [LICENSE_ACE](https://github.com/GlowstoneMC/Site/blob/falcon/LICENSE_ACE).

Setting up
----------

1. Fill out your `config.yml` based on `config.example.yml`
    * Ensure the database you gave above exists
2. Run `python3 tools.py run-migrations`
3. Install and set up [Celery](http://www.celeryproject.org/)
    * You can give `ultros_site.tasks.__main__:app` for the Celery app
4. Set up your WSGI server of choice; the app is `ultros_site.__main__.app`
5. On your webserver, make sure you serve `/static` directly instead of proxying it to the WSGI app

Running migrations
------------------

Simply run `python3 tools.py run-migrations` again to make sure your database is up to date after every pull.

Developers: Modifying the database
-----------------------------------

If you're going to change the database, do the following:

1. Before you edit or create a schema, ensure you run `python3 tools.py run-migrations` so that you're up-to-date
    * This is important as Alembic uses the current state of the database to generate migrations
2. Go ahead and make your edits
3. Run `python3 tools.py create-migrations "Summary of the migrations"`
4. Run `python3 tools.py run-migrations` to update your local database with the migration you just created

Advanced Alembic usage
----------------------

If you need to run Alembic manually, please ensure that you set your PYTHONPATH variable to `.` (or add `.` to it),
otherwise the Alembic environment will not be able to import the database metadata and will fail to load.
