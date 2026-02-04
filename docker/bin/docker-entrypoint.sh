#!/bin/bash -e

export MEDIA_ROOT="${MEDIA_ROOT:-/var/run/app/media}"
export STATIC_ROOT="${STATIC_ROOT:-/var/run/app/static}"
export UWSGI_PROCESSES="${UWSGI_PROCESSES:-"4"}"
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-"bitcaster.config.settings"}"
mkdir -p "${MEDIA_ROOT}" "${STATIC_ROOT}" || echo "Cannot create dirs ${MEDIA_ROOT} ${STATIC_ROOT}"


case "$1" in
    worker)
      bc run
      ;;
    scheduler)
      bc scheduler
      ;;
    run)
      django-admin check --deploy
      django-admin upgrade
  		uwsgi --ini /conf/uwsgi.ini
	    ;;
esac

exec "$@"
