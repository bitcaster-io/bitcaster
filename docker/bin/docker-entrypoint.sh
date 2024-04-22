#!/bin/sh -e

alias env='env|sort'

MEDIA_ROOT="${MEDIA_ROOT:-/var/media}"
STATIC_ROOT="${STATIC_ROOT:-/var/static}"


mkdir -p /var/run "${MEDIA_ROOT}" "${STATIC_ROOT}"

echo "Executing '$1'..."
echo "INIT_RUN_UPGRADE         '$INIT_RUN_UPGRADE'"
echo "  INIT_RUN_CHECK         '$INIT_RUN_CHECK'"
echo "  INIT_RUN_COLLECTSTATIC '$INIT_RUN_COLLECTSTATIC'"
echo "  INIT_RUN_MIGRATATIONS  '$INIT_RUN_MIGRATATIONS'"
echo "INIT_START_BOB         '$INIT_START_BOB'"
echo "INIT_START_DAPHNE      '$INIT_START_DAPHNE'"
echo "INIT_START_CELERY      '$INIT_START_CELERY'"
echo "INIT_START_BEAT        '$INIT_START_BEAT'"
echo "INIT_START_FLOWER      '$INIT_START_FLOWER'"

case "$1" in
    run)
      if [ "$INIT_RUN_CHECK" = "1" ];then
        django-admin check --deploy
      fi
      OPTS="--no-check -v 1"
      if [ "$INIT_RUN_UPGRADE" = "1" ];then
        if [ "$INIT_RUN_COLLECTSTATIC" != "1" ];then
          OPTS="$OPTS --no-static"
        fi
        if [ "$INIT_RUN_MIGRATATIONS" != "1" ];then
          OPTS="$OPTS --no-migrate"
        fi
        echo "Running 'upgrade $OPTS'"
        django-admin upgrade $OPTS
      fi
      exec circusd /conf/circus.conf
      ;;
    dev)
      until pg_isready -h db -p 5432;
        do echo "waiting for database"; sleep 2; done;
      django-admin collectstatic --no-input
      django-admin migrate
      django-admin runserver 0.0.0.0:8000
      ;;
    *)
      exec "$@"
      ;;
esac
