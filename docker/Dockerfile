FROM pstauffer/curl:latest as builder
ARG DEVELOP
ARG GITHUB_CREDENTIALS
ARG VERSION

RUN mkdir /code
ADD . /code

RUN set -o pipefail && if [ "${DEVELOP}" = "1" ]; then \
    echo "${VERSION}-develop"; \
    else \
    echo "Download package: https://github.com/bitcaster-io/bitcaster/archive/${VERSION}.tar.gz" \
    && curl ${GITHUB_CREDENTIALS}: -L "https://github.com/bitcaster-io/bitcaster/archive/${VERSION}.tar.gz" | tar -xzf - --strip-components=1; \
    fi

FROM python:3.6.7-slim as base
RUN apt-get update \
 	&& apt-get install -y --no-install-recommends \
 	    gcc \
 	    gdal-bin \
 	    python-dev

RUN pip install pip==18.0 pipenv --upgrade \
    && adduser --system bitcaster

FROM base
COPY --from=builder /code /code

LABEL org.label.name="Bitcaster" \
      org.label.maintainer="bitcaster@os4d.org" \
      org.label.description="" \
      org.label.url="https://bitcaster.io/" \
      org.label.vcs-url="https://github.com/bitcaster-io/bitcaster" \
      org.label.version=$VERSION


ARG BUILD_DATE
ARG PIPENV_ARGS
ARG VERSION

ENV VERSION ${VERSION}

ENV PIPENV_PYPI_MIRROR ${PIPENV_PYPI_MIRROR}
ENV PIPENV_ARGS ${PIPENV_ARGS}
ENV HOME /var/bitcaster/
ENV PIPSI_HOME=/usr/local/pipsi/environments
ENV PIPSI_BIN_DIR=/usr/local/bin
ENV PYTHONUNBUFFERED 1
ENV GUNICORN_CMD_ARGS "-b 0.0.0.0:8000 \
--chdir /var/bitcaster \
--access-logfile - \
--access-logformat \"%(h)s %(l)s %(u)s %(t)s '%(r)s' %(s)s\" "

ENV BITCASTER_MEDIA_ROOT $HOME/media
ENV BITCASTER_STATIC_ROOT $HOME/static
ENV BITCASTER_CONF $HOME/conf/config
ENV BITCASTER_DATABASE_URL ""
ENV BITCASTER_CELERY_BROKER_URL ""
ENV BITCASTER_REDIS_CACHE_URL ""
ENV BITCASTER_REDIS_LOCK_URL ""

RUN mkdir -p \
    /var/bitcaster/ \
    && chown bitcaster /var/bitcaster/ \
    && pip install pip==18.0 pipenv --upgrade

WORKDIR /code

RUN set -ex \
    ls -al /code \
    && pipenv install --verbose --system --deploy --ignore-pipfile $PIPENV_ARGS

RUN pip install . \
    && bitcaster plugin install --from-dir plugins/ -r \
    && rm -fr /code


#RUN apk del .build-deps \
#    && rm -rf /var/cache/apk/* \
#    && rm -fr /root/.cache/

WORKDIR /var/bitcaster

EXPOSE 8000

USER bitcaster

ADD docker/entrypoint.sh /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["docker-entrypoint.sh"]

CMD ["bitcaster"]
