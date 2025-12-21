#!/bin/bash -e

export MEDIA_ROOT="${MEDIA_ROOT:-/var/run/app/media}"
export STATIC_ROOT="${STATIC_ROOT:-/var/run/app/static}"
export UWSGI_PROCESSES="${UWSGI_PROCESSES:-"4"}"
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-"bitcaster.config.settings"}"
mkdir -p "${MEDIA_ROOT}" "${STATIC_ROOT}" || echo "Cannot create dirs ${MEDIA_ROOT} ${STATIC_ROOT}"

echo $STATIC_ROOT
echo $MEDIA_ROOT

case "$1" in
    worker)
      bitcaster celery -A bitcaster.config.celery worker -E --loglevel=ERROR --concurrency=4
      ;;
    beat)
      celery -A bitcaster.config.celery beat --loglevel=ERROR --scheduler django_celery_beat.schedulers:DatabaseScheduler
      ;;
    run)
      django-admin check --deploy
      django-admin upgrade
  		uwsgi --ini /conf/uwsgi.ini
	    ;;
esac

exec "$@"
