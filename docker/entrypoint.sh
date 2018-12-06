#!/bin/bash -e
set -e

mkdir -p /var/bitcaster/{static,log,conf,run}
rm -f /var/datamart/run/*


if [[ "$*" == "workers" ]];then
    django-admin db-isready --wait --timeout 60 --sleep 5
    django-admin db-isready --wait --timeout 300  --sleep 5 --connection etools
    celery worker -A etools_datamart --loglevel=DEBUG --concurrency=4 --purge --pidfile run/celery.pid
elif [[ "$*" == "beat" ]];then
    celery beat -A etools_datamart.celery --loglevel=DEBUG --pidfile run/celerybeat.pid
elif [[ "$*" == "bitcaster" ]];then
    django-admin db-isready --wait --timeout 60
    django-admin check --deploy
    django-admin init-setup --all --verbosity 1
    django-admin db-isready --wait --timeout 300 --connection etools
    gunicorn -b 0.0.0.0:8000 etools_datamart.config.wsgi
else
    exec "$@"
fi
