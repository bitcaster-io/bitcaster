# Bitcaster dev environment
#
# NOTE: Do NOT use this in production!
#
# Instructions:
#
#   Build the container:
#     $ docker build --rm --squash -t bitcaster:beta -f Dockerfile.dev .
#   Bootstrap the container:
#     $ docker run --name=bitcaster-beta -p 8000:8000 -it -v /data/storage/bitcaster/etc/:/etc/bitcaster -v /data/storage/bitcaster/var/bitcaster/:/var/bitcaster bitcaster:beta
#   Run the container:
#     $ docker start bitcaster-beta
#   Attach into the container:
#     $ docker exec -it bitcaster-beta bash
#   Run devserver:
#     $ docker exec -it bitcaster-beta bitcaster devserver 0.0.0.0:8000
#   Stop container:
#     $ docker stop bitcaster-beta
#   Remove container:
#     $ docker rm -f bitcaster-beta

FROM python:3.6
ENV PYTHONUNBUFFERED 1
ENV PG_MAJOR 9.6
ENV PG_VERSION 9.6.*
ENV DATABASE_NAME bitcaster
ENV NGINX_VERSION 1.13.7-1~stretch
ENV NJS_VERSION   1.13.7.0.1.15-1~stretch

RUN apt-get update && apt-get install -y --no-install-recommends \
        ntp \
        vim \
    && rm -rf /var/lib/apt/lists/*

# make the "en_US.UTF-8" locale so postgres will be utf-8 enabled by default
RUN apt-get update && apt-get install -y locales && rm -rf /var/lib/apt/lists/* \
    && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG en_US.utf8

RUN apt-key adv --keyserver ha.pool.sks-keyservers.net --recv-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8

ENV BITCASTER_MEDIA_ROOT /var/bitcaster/media
ENV BITCASTER_STATIC_ROOT /var/bitcaster/static

ENV BITCASTER_DATABASE_HOST db
ENV BITCASTER_REDIS_CACHE_URL redis://redis:6379/0
ENV BITCASTER_REDIS_LOCK_URL redis://redis:6379/1
ENV BITCASTER_CELERY_BROKER_URL redis://redis:6379/2
ENV BITCASTER_DATABASE_URL psql://postgres:@db:5432/bitcaster

ENV BITCASTER_CONF_DIR /etc/bitcaster/
ENV BITCASTER_CONF ${BITCASTER_CONF_DIR}conf
RUN mkdir -p /usr/src/bitcaster -m 770
RUN mkdir -p ${BITCASTER_MEDIA_ROOT} -m 770
RUN mkdir -p ${BITCASTER_STATIC_ROOT} -m 770
RUN mkdir -p ${BITCASTER_CONF_DIR} -m 770
RUN touch ${BITCASTER_CONF}
COPY dist /cache
RUN pip install bitcaster \
    bitcaster-facebook \
    bitcaster-gmail \
    bitcaster-hangout \
    bitcaster-plivo \
    bitcaster-skype \
    bitcaster-slack-webhook \
    bitcaster-twilio \
    bitcaster-twitter \
    bitcaster-twitter-message \
    bitcaster-xmpp \
    --find-links file:///cache \
    --cache-dir /cache


WORKDIR /usr/src/bitcaster

COPY docker/entrypoint.sh /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]

EXPOSE 8000
CMD [ "bash" ]
