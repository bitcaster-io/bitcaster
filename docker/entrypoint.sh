#!/bin/sh -e

mkdir -p /backups /var/bitcaster/run ${BITCASTER_MEDIA_ROOT} ${BITCASTER_STATIC_ROOT}
chown bitcaster:bitcaster -R /var/bitcaster/ /backups
chmod 775 /var/bitcaster/ /backups
chmod g+s /var/bitcaster/ /backups

rm -f /var/bitcaster/run/*


if [[ "$*" == "workers" ]];then
    bitcaster check --deploy --wait-services
    exec gosu bitcaster bitcaster run worker --loglevel=DEBUG --concurrency=4 --pidfile run/celery.pid
elif [[ "$*" == "beat" ]];then
    bitcaster check --deploy --wait-services
    exec gosu bitcaster bitcaster run beat --loglevel=DEBUG --pidfile run/celerybeat.pid
elif [[ "$*" == "bitcaster" ]];then
    bitcaster check --deploy --wait-services
    bitcaster upgrade --static --migrate --no-input
    exec gosu bitcaster gunicorn -b 0.0.0.0:8000 bitcaster.config.wsgi
elif [[ "$*" == "stack" ]];then
    bitcaster check --deploy --wait-services
    bitcaster upgrade --static --migrate --no-input
    exec gosu bitcaster circusd /etc/circus.conf
else
    exec "$@"
fi
