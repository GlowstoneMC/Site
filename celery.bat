@ECHO OFF
py -3 -m celery -A "ultros_site.tasks.__main__:app" worker -f celery.out -l info --concurrency=1