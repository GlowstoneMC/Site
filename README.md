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

Step-by-step instructions
-------------------------

If you haven't worked with this kind of stack before, here's how you set up a development environment.

* Install prerequisites
    * Python 3.6
    * `python3 -m pip install requirements.txt`
        * If you're on Windows, `python3 -m pip install celery==3.1.25` (They dropped support for Windows in 4.x)
    * `python3 -m pip install requirements-test.txt`
    * Redis
    * RabbitMQ
    * PostgreSQL Server
        * Optionally, install PGAdmin as well - we recommend PGAdmin 3 over 4 as it's much faster and easier to use
* Copy `config.yml.example` to `config.yml`
* Edit your machine's HOSTS file to point the hostname `storage` to `127.0.0.1` (or wherever you're running RabbitMQ and Redis)
* Set up your runs - make sure you run everything from the root directory of the repo (the folder containing the README)
    * To start your Celery workers: `celery -A ultros_site.tasks.__main__:app worker`
    * To start the webapp with the Waitress development server: `python3 -m ultros_site --debug`
* Before you commit your changes, run `flake8 ultros_site` from the repo root - this will check that all the Python code meets our coding standards

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
