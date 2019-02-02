FROM pstauffer/curl:latest as retriever
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

FROM python:3.6.7-slim-stretch as base
RUN apt-get update \
 	&& apt-get install -y --no-install-recommends \
 	    gcc \
 	    gdal-bin \
 	    python-dev

RUN adduser --system bitcaster

FROM base
COPY --from=retriever /code /code
ARG BUILD_DATE
ARG PIPENV_ARGS
ARG VERSION
ENV VERSION ${VERSION}

LABEL org.label.name="Bitcaster" \
      org.label.maintainer="bitcaster@os4d.org" \
      org.label.description="Bitcaster is a system-to-user signal-to-message notification system." \
      org.label.url="https://bitcaster.io/" \
      org.label.vcs-url="https://github.com/bitcaster-io/bitcaster" \
      org.label.version=${VERSION} \
      org.label.date=${BUILD_DATE}

ENV PIPENV_PYPI_MIRROR ${PIPENV_PYPI_MIRROR}
ENV PIPENV_ARGS ${PIPENV_ARGS}
ENV HOME /var/bitcaster
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
ENV BITCASTER_LOG_LEVEL "ERROR"


WORKDIR /code

RUN set -ex \
    && ls -al /code \
    && pip install pip==18.0 pipenv --upgrade \
    && mkdir -p /var/bitcaster/ \
    && chown bitcaster /var/bitcaster/ \
    && pipenv install --verbose --system --deploy --ignore-pipfile $PIPENV_ARGS

RUN pip --disable-pip-version-check install .
RUN for dir in plugins/*;do pip --disable-pip-version-check install $dir; done;
RUN pip list | grep bitcaster

WORKDIR /var/bitcaster

RUN rm -fr /code \
    && rm -fr /var/bitcaster/.cache \
    && apt-get purge --auto-remove -y \
        gcc \
        mysql-common \
        python-dev

USER bitcaster

EXPOSE 8000
EXPOSE 5555
EXPOSE 6379

ADD docker/entrypoint.sh /usr/local/bin/docker-entrypoint.sh
ADD docker/circus.conf /etc/circus.conf

ENTRYPOINT ["docker-entrypoint.sh"]

CMD ["bitcaster"]
