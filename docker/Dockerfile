FROM bitcaster/bitcaster-0.4:base

ARG BUILD_DATE
ARG VERSION
ARG DEVELOP

ENV DEVELOP=${DEVELOP}

RUN mkdir -p /code
COPY . /code
WORKDIR /code
RUN echo $DEVELOP
RUN set -o pipefail && \
    if [ "${DEVELOP}" = "1" ]; then \
    echo "${VERSION}-develop"; \
    else \
    echo "Download package: https://github.com/bitcaster-io/bitcaster/archive/${VERSION}.tar.gz" \
    && curl -L "https://github.com/bitcaster-io/bitcaster/archive/${VERSION}.tar.gz" | tar -xzf - --strip-components=1; \
    fi

RUN set -ex \
    ls -al /code \
    && pip3 install .

LABEL org.label.name="Bitcaster" \
      org.label.maintainer="bitcaster@os4d.org" \
      org.label.description="Bitcaster is a system-to-user signal-to-message notification system." \
      org.label.url="https://bitcaster.io/" \
      org.label.vcs-url="https://github.com/bitcaster-io/bitcaster" \
      org.label.version=${VERSION} \
      org.label.date=${BUILD_DATE}

ENV DOCKER_BUILD ${BUILD_DATE}
ENV VERSION ${VERSION}
ENV PIPENV_ARGS ${PIPENV_ARGS}
ENV PYTHONUNBUFFERED 1
ENV GUNICORN_CMD_ARGS "-b 0.0.0.0:8000 \
--chdir /var/bitcaster \
--access-logfile - \
--access-logformat \"%(h)s %(l)s %(u)s %(t)s '%(r)s' %(s)s\" "
ENV DJANGO_SETTINGS_MODULE "bitcaster.config.settings"
ENV BITCASTER_SECRET_KEY "secret-key-just-for-build"
ENV BITCASTER_MEDIA_ROOT /var/bitcaster/media
ENV BITCASTER_STATIC_ROOT /var/bitcaster/static
ENV BITCASTER_DATABASE_URL ""
ENV BITCASTER_CELERY_BROKER_URL "redis://localhost:6379/1"
ENV BITCASTER_REDIS_CACHE_URL "redis://localhost:6379/1"
ENV BITCASTER_REDIS_LOCK_URL "redis://localhost:6379/1"
ENV BITCASTER_LOG_LEVEL "ERROR"
ENV BITCASTER_ENABLE_IMPERSONATE "0"
ENV BITCASTER_ADVANCED_MODE "0"

EXPOSE 8000

RUN apk add --no-cache --virtual .run-deps \
        --repository http://dl-cdn.alpinelinux.org/alpine/edge/main \
        --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \
        gosu \
        libpq \
        libxslt \
        libzmq \
        jpeg

COPY docker/entrypoint.sh /usr/local/bin/docker-entrypoint.sh
COPY docker/circus.conf /etc/circus.conf


RUN addgroup --gid 1024 bitcaster \
    && adduser --disabled-password --ingroup bitcaster -S bitcaster

WORKDIR /var/bitcaster

RUN django-admin collectstatic

ENTRYPOINT ["docker-entrypoint.sh"]

CMD ["bitcaster"]
