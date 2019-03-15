FROM python:3.6.8-alpine3.8 as base

ARG BUILD_DATE
ARG PIPENV_ARGS
ARG VERSION
ARG DEVELOP

ENV CPLUS_INCLUDE_PATH /usr/include/libxml2/
ENV C_INCLUDE_PATH /usr/include/libxml2/

RUN apk add --no-cache --virtual .build-deps \
        gcc \
        musl-dev \
        python3-dev \
        libffi-dev \
        libressl-dev \
        libxml2-dev \
        libxslt-dev \
        jpeg-dev \
        linux-headers \
        postgresql-dev \
        zeromq-dev

#RUN apk add --no-cache --virtual .run-deps \
#        libpq \
#        libxslt \
#        libzmq \
#        jpeg

RUN mkdir -p /code
COPY . /code
WORKDIR /code

RUN set -o pipefail && if [ "${DEVELOP}" = "1" ]; then \
    echo "${VERSION}-develop"; \
    else \
    echo "Download package: https://github.com/bitcaster-io/bitcaster/archive/${VERSION}.tar.gz" \
    && curl -L "https://github.com/bitcaster-io/bitcaster/archive/${VERSION}.tar.gz" | tar -xzf - --strip-components=1; \
    fi

RUN set -ex \
    ls -al /code \
    && pip install pip pipenv \
    && pipenv install --verbose --system --deploy --ignore-pipfile $PIPENV_ARGS \
    && pip3 install .

FROM python:3.6.8-alpine3.8
COPY --from=0 /usr/local/lib/python3.6/ /usr/local/lib/python3.6/
COPY --from=0 /usr/local/bin /usr/local/bin

LABEL org.label.name="Bitcaster" \
      org.label.maintainer="bitcaster@os4d.org" \
      org.label.description="Bitcaster is a system-to-user signal-to-message notification system." \
      org.label.url="https://bitcaster.io/" \
      org.label.vcs-url="https://github.com/bitcaster-io/bitcaster" \
      org.label.version=${VERSION} \
      org.label.date=${BUILD_DATE}

ENV VERSION ${VERSION}
ENV PIPENV_ARGS ${PIPENV_ARGS}
ENV PYTHONUNBUFFERED 1
ENV GUNICORN_CMD_ARGS "-b 0.0.0.0:8000 \
--chdir /var/bitcaster \
--access-logfile - \
--access-logformat \"%(h)s %(l)s %(u)s %(t)s '%(r)s' %(s)s\" "

ENV BITCASTER_MEDIA_ROOT /var/bitcaster/media
ENV BITCASTER_STATIC_ROOT /var/bitcaster/static
ENV BITCASTER_CONF $HOME/conf/config
ENV BITCASTER_DATABASE_URL ""
ENV BITCASTER_CELERY_BROKER_URL ""
ENV BITCASTER_REDIS_CACHE_URL ""
ENV BITCASTER_REDIS_LOCK_URL ""
ENV BITCASTER_LOG_LEVEL "ERROR"


EXPOSE 8000
#  clean all and removes all non needed files
#RUN apk del .build-deps
#RUN rm -rf /var/cache/apk/* \
#    rm -fr /root/.cache/ \
#    rm -fr /code \
#    rm -fr /var/bitcaster/.cache/ \
#    rm -fr /usr/include/ \
#    pip uninstall pipenv

RUN apk add --no-cache --virtual .run-deps \
        libpq \
        libxslt \
        libzmq \
        jpeg
#
#RUN find /usr/local/lib/python3.6/ -name *.pyc | xargs rm -f \
#    && python -O -m compileall -x _plugin_template.* -fqb /usr/local/lib/python3.6/ \
#    && find /usr/local/lib/python3.6/ -name *.py | xargs rm -f

# end clean

COPY docker/entrypoint.sh /usr/local/bin/docker-entrypoint.sh
COPY docker/circus.conf /etc/circus.conf

RUN adduser -S bitcaster \
    && mkdir -p /var/bitcaster \
    && chown bitcaster /var/bitcaster/

WORKDIR /var/bitcaster
USER bitcaster

ENTRYPOINT ["docker-entrypoint.sh"]

CMD ["bitcaster"]
