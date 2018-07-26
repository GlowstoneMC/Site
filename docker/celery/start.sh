#! /bin/sh
export AUTOSCALE_MAX=8
export AUTOSCALE_MIN=4
export CELERY_APP="ultros_site.tasks.__main__:app"
export LOG_LEVEL="warning"
export TIME_LIMIT="300"
export WORKDIR="/app"

celery worker -A ${CELERY_APP} --autoscale ${AUTOSCALE_MAX},${AUTOSCALE_MIN} --beat --time-limit ${TIME_LIMIT} --workdir=${WORKDIR} -l ${LOG_LEVEL}
