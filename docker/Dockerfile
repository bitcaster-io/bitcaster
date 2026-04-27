FROM python:3.13-slim-bookworm AS base_os
ARG VERSION
ARG GIT_SHA
ARG BUILD_DATE

RUN set -x \
  && apt-get update && apt-get install -y --no-install-recommends debian-archive-keyring \
  && runtimeDeps=" \
    nginx \
    gettext \
    libmagic1 \
    libxml2 \
    libexpat1 \
  " \
  && buildDeps=" \
wget \
" \
  && apt-get update && apt-get install -y --no-install-recommends ${buildDeps} ${runtimeDeps} \
  && apt-get purge -y --auto-remove $buildDeps

RUN groupadd --gid 1024 os4d \
    && adduser --disabled-login --disabled-password --no-create-home --ingroup os4d -q bitcaster

# ------- deps -------
FROM base_os AS deps
RUN set -x \
    && buildDeps="build-essential \
cmake \
curl \
gcc \
git \
libfontconfig1 \
libgconf-2-4 \
libglib2.0-0 \
libnss3 \
libssl-dev \
libxml2-dev  \
python3-dev \
zlib1g-dev  \
" \
    && apt-get update \
    && apt-get install -y --no-install-recommends $buildDeps \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uwsgi uv

# ------- builder -------
FROM deps AS builder
ARG VERSION
ARG GIT_SHA
ARG BUILD_DATE
ENV VIRTUAL_ENV=/venv \
    UV_PROJECT_ENVIRONMENT=/venv \
    HATCH_VCS_VERSION=${VERSION} \
    SETUPTOOLS_SCM_PRETEND_VERSION=${VERSION}

RUN <<EOF cat> /RELEASE
{"version": "$VERSION",
  "commit": "$GIT_SHA",
  "date": "$BUILD_DATE"
}
EOF
RUN mkdir /code /venv

WORKDIR /code
COPY . /code

RUN ls -al /code/src/
RUN uv venv --no-cache $VIRTUAL_ENV \
    && uv sync --no-dev --frozen --no-editable --no-cache \
    && git status \
    && uv build

FROM base_os AS dist
ARG VERSION
ARG GIT_SHA
ARG BUILD_DATE
ADD docker/conf /conf/
ADD docker/bin/* /usr/local/bin/

COPY --from=builder /usr/local/bin/uwsgi /usr/local/bin/
COPY --from=builder /venv /venv
RUN mkdir -p /var/storage/media/ /var/storage/static/ \
    && chown -R bitcaster /var/storage/

ENV PATH=/venv/bin:/usr/local/bin/:/usr/bin:/bin:/usr/sbin \
    VERSION=$VERSION \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE="bitcaster.config.settings" \
    STATIC_URL="/static/" \
    PYTHONPATH="/venv/lib/python3.13/site-packages"\
    GIT_SHA=$GIT_SHA \
    PGSSLCERT="/tmp/postgresql.crt" \
    UWSGI_PROCESSES=4

EXPOSE 8000
USER bitcaster

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["run"]

LABEL maintainer="bitcaster@bitcaster.io"
LABEL org.opencontainers.image.authors="bitcaster@bitcaster.io"
LABEL org.opencontainers.image.created="$BUILD_DATE"
LABEL org.opencontainers.image.description="Bitcaster"
LABEL org.opencontainers.image.documentation="https://github.com/bitcaster-io/bitcaster"
LABEL org.opencontainers.image.licenses="https://github.com/bitcaster-io/bitcaster/blob/${GIT_SHA:-master}/LICENSE.md"
LABEL org.opencontainers.image.revision=$GIT_SHA
LABEL org.opencontainers.image.source="https://github.com/bitcaster-io/bitcaster/tree/${GIT_SHA:-master}/"
LABEL org.opencontainers.image.title="Bitcaster"
LABEL org.opencontainers.image.version="$VERSION"
LABEL org.opencontainers.image.url="https://bitcaster.io/"
LABEL org.opencontainers.image.vendor="OS4D ltd"
