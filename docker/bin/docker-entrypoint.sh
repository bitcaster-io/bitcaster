#!/bin/bash -e

export MEDIA_ROOT="${MEDIA_ROOT:-/var/run/app/media}"
export STATIC_ROOT="${STATIC_ROOT:-/var/run/app/static}"
export UWSGI_PROCESSES="${UWSGI_PROCESSES:-"4"}"
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-"bitcaster.config.settings"}"
mkdir -p "${MEDIA_ROOT}" "${STATIC_ROOT}" || echo "Cannot create dirs ${MEDIA_ROOT} ${STATIC_ROOT}"

echo $STATIC_ROOT
echo $MEDIA_ROOT

if [ -d "${STATIC_ROOT}" ];then
  chown -R user:app ${STATIC_ROOT}
fi
if [ -d "${MEDIA_ROOT}" ];then
  chown -R user:app ${MEDIA_ROOT}
fi

case "$1" in
    upgrade)
      django-admin check --deploy
	    set -- tini -- "$@"
      set -- gosu user:app django-admin upgrade
      ;;
    config)
      echo "CMD $@"
      django-admin env
      exit 0
      ;;
    flower)
	    set -- tini -- "$@"
      set -- gosu user:app celery -A bitcaster.config.celery flower
      ;;
    worker)
	    set -- tini -- "$@"
      set -- gosu user:app celery -A bitcaster.config.celery worker -E --loglevel=ERROR --concurrency=4
      ;;
    beat)
	    set -- tini -- "$@"
      set -- gosu user:app celery -A bitcaster.config.celery beat --loglevel=ERROR --scheduler django_celery_beat.schedulers:DatabaseScheduler
      ;;
    run)
      django-admin check --deploy
      django-admin upgrade
      chown -R user:app ${STATIC_ROOT}
	    set -- tini -- "$@"
  		set -- gosu user:app uwsgi --ini /conf/uwsgi.ini
	    ;;
esac

exec "$@"
