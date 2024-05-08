# syntax=docker/dockerfile:1.3
ARG PYTHON_VER=3.12
ARG PKG_DIR=/code/__pypackages__/$PYTHON_VER/lib
ARG BUILD_DATE
ARG CHECKSUM

FROM python:${PYTHON_VER}-slim-bullseye AS python

FROM python AS base
ARG PKG_DIR
ENV ADMINS="" \
    BUILD_DATE=$BUILD_DATE \
    CHANNEL_URLS=""\
    CHECKSUM=$CHECKSUM \
    CI_BUILD_ID=$CI_BUILD_ID \
    CI_COMMIT_SHORT_SHA=$CI_COMMIT_SHORT_SHA \
    CI_JOB_URL=$CI_JOB_URL \
    DATABASE_URL="" \
    DEV_FOOTER_INFO="" \
    DJANGO_SETTINGS_MODULE="bitcaster.config.settings" \
    DJSTRIPE_WEBHOOK_VALIDATION=""\
    DOCKER_TAG=$DOCKER_TAG \
    INIT_RUN_CHECK=1 \
    INIT_RUN_COLLECTSTATIC=1 \
    INIT_RUN_MIGRATATIONS=1 \
    INIT_RUN_UPGRADE=0 \
    INIT_START_BEAT=0 \
    INIT_START_BOB=0 \
    INIT_START_CELERY=0 \
    INIT_START_DAPHNE=0 \
    INIT_START_FLOWER=0 \
    LOG_LEVEL="ERROR" \
    MEDIA_ROOT="/var/bitcaster/media" \
    PKG_DIR=$PKG_DIR \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=$PKG_DIR:/code/src/ \
    PYTHONUNBUFFERED=1 \
    SECRET_KEY="secret-key-just-for-build" \
    SENTRY_DSN="" \
    SOCIAL_AUTH_GOOGLE_OAUTH_KEY=""\
    SOCIAL_AUTH_GOOGLE_OAUTH_SECRET=""\
    STATIC_ROOT="/var/bitcaster/static" \
    STATIC_URL="" \
    UWSGI_PROCESSES=4 \
    VERSION=${VERSION}
ENV PYTHONPATH=$PKG_DIR:/code/src/ \
    PATH=${PATH}:$PKG_DIR/../bin/

RUN ln -s -f /bin/true /usr/bin/chfn \
    && groupadd --gid 1024 bitcaster \
    && adduser --disabled-login --disabled-password --no-create-home --ingroup bitcaster -q www


FROM python AS cache
ARG PKG_DIR
ENV BUILD_DATE=$BUILD_DATE \
    VERSION=$VERSION \
    PYTHONDONTWRITEBYTECODE=1
ENV buildDeps="build-essential gcc libjpeg-dev zlib1g-dev libffi-dev libssl-dev libpq-dev "
ENV runtimeDeps="postgresql-client libmagic"
RUN rm -f /etc/apt/apt.conf.d/docker-clean \
    && echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

RUN --mount=target=/var/lib/apt/lists,type=cache,sharing=locked \
    --mount=target=/var/cache/apt,type=cache,sharing=locked \
    apt-get update

RUN --mount=target=/var/lib/apt/lists,type=cache,sharing=locked \
    --mount=target=/var/cache/apt,type=cache,sharing=locked \
    apt-get install -y --no-install-recommends $buildDeps

RUN --mount=target=/var/lib/apt/lists,type=cache,sharing=locked \
    --mount=target=/var/cache/apt,type=cache,sharing=locked \
    apt-get install -y --no-install-recommends $runtimeDeps

RUN rm -rf /var/lib/apt/lists/*
RUN pip install -U pip setuptools && pip install pdm

FROM cache AS builder
ARG PKG_DIR
ARG CHECKSUM
WORKDIR /code/
COPY pyproject.toml pdm.lock README.md /code/
RUN mkdir __pypackages__ \
    && pdm sync --prod --no-editable --no-self

RUN echo $CHECKSUM > /CHECKSUM


FROM builder AS builder-test
ARG PKG_DIR
WORKDIR /code/
ENV PYTHONPATH=$PKG_DIR:/code/src/ \
    PATH=${PATH}:$PKG_DIR/../bin/

RUN pdm sync --no-editable --no-self


FROM base AS dist
ARG PKG_DIR
COPY docker/bin/* /usr/local/bin/
COPY docker/conf/* /conf/
WORKDIR /code/
COPY --from=builder /code/__pypackages__ /code/__pypackages__
COPY --from=builder /CHECKSUM /CHECKSUM
COPY ./src /code/src

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["run"]


FROM base AS test
ARG PKG_DIR
COPY docker/bin/* /usr/local/bin/
COPY docker/conf/* /conf/
WORKDIR /code/
COPY --from=builder-test /code/__pypackages__ /code/__pypackages__
COPY --from=builder /CHECKSUM /CHECKSUM
COPY . /code/

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["run"]

#COPY docker/bin/* /usr/local/bin/
#COPY docker/conf/* /conf/
#COPY pyproject.toml pdm.lock README.md /code/
#
#ENTRYPOINT ["docker-entrypoint.sh"]
#CMD ["run"]
#
#
#FROM builder as builder-test
#ARG PKG_DIR
#ENV PYTHONPATH=$PKG_DIR:/code/src/
#ENV PATH=${PATH}:$PKG_DIR/../bin/
#
#RUN ls -al \
#    && pdm config python.use_venv False \
#    && pdm sync --no-editable -vv -g
#
#
## Test image
#FROM python as test
#ARG PKG_DIR
#ENV PYTHONPATH=$PKG_DIR:/code/src/
#ENV PATH=${PATH}:$PKG_DIR/../bin/
#COPY --from=builder-test /code/__pypackages__ /code/
#
#COPY . /code/
#
##
## Dist image
#FROM python as dist
#ARG PKG_DIR
#ENV PYTHONPATH=$PKG_DIR:/code/src/ \
#    PATH=${PATH}:$PKG_DIR/../bin/
#COPY docker/bin/* /usr/local/bin/
#COPY docker/conf/* /conf/
#WORKDIR /code/
#COPY --from=builder /code/__pypackages__ /code/__pypackages__
#COPY ./src /code/
#
#ENTRYPOINT ["docker-entrypoint.sh"]
