#!/bin/bash -e
set -e

mkdir -p /var/bitcaster/{log,conf,run} ${BITCASTER_MEDIA_ROOT} ${BITCASTER_STATIC_ROOT}
rm -f /var/datamart/run/*


if [[ "$*" == "workers" ]];then
    bitcaster check --deploy
    celery worker -A bitcaster --loglevel=DEBUG --concurrency=4 --purge --pidfile run/celery.pid
elif [[ "$*" == "beat" ]];then
    bitcaster check --deploy
    celery beat -A bitcaster --loglevel=DEBUG --pidfile run/celerybeat.pid
elif [[ "$*" == "bitcaster" ]];then
    bitcaster check --deploy
    bitcaster upgrade --no-input
    gunicorn -b 0.0.0.0:8000 bitcaster.config.wsgi
elif [[ "$*" == "stack" ]];then
    bitcaster check --deploy
    bitcaster upgrade --no-input
    exec supervisord --nodaemon -c /etc/supervisord.conf
else
    exec "$@"
fi
