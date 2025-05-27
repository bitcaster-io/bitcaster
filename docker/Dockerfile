FROM python:3.13-slim-bookworm AS base_os
ARG GOSU_VERSION=1.17
ARG GOSU_SHA256=bbc4136d03ab138b1ad66fa4fc051bafc6cc7ffae632b069a53657279a450de3


RUN set -x \
  && runtimeDeps=" \
    libmagic1 \
    libxml2 \
  " \
  && buildDeps=" \
wget \
" \
  && apt-get update && apt-get install -y --no-install-recommends ${buildDeps} ${runtimeDeps} \
  && rm -rf /var/lib/apt/lists/* \
  && wget --quiet -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-amd64" \
  && echo "$GOSU_SHA256 /usr/local/bin/gosu" | sha256sum --check --status \
  && chmod +x /usr/local/bin/gosu \
  && apt-get purge -y --auto-remove $buildDeps

RUN groupadd --gid 1024 bitcaster-io \
    && adduser --disabled-login --disabled-password --no-create-home --ingroup bitcaster-io -q bitcaster


# ------- builder -------
FROM base_os AS builder
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

RUN apt-get update && \
    apt-get install -y --no-install-recommends gnupg wget curl unzip && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends google-chrome-stable && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/* && \
    CHROME_VERSION=$(google-chrome --product-version) && \
    wget -q --continue -P /chromedriver "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROME_VERSION/linux64/chromedriver-linux64.zip" && \
    unzip /chromedriver/chromedriver* -d /usr/local/bin/ && \
    rm -rf /chromedriver

RUN pip install uv uwsgi

#
#WORKDIR /app
#RUN --mount=type=cache,target=/root/.uv-cache \
#    --mount=type=bind,source=uv.lock,target=/app/uv.lock \
#    --mount=type=bind,source=pyproject.toml,target=/app/pyproject.toml \
#    --mount=type=bind,source=MANIFEST.in,target=/app/MANIFEST.in \
#    --mount=type=bind,source=README.md,target=/app/README.md \
#    --mount=type=bind,source=./src/bitcaster,target=/app/src/bitcaster \
#    uv sync --cache-dir=/root/.uv-cache \
#        --python=/usr/local/bin//python \
#        --python-preference=system \
#        --no-dev --no-editable --frozen --extra distribution


# ------- tests -------
FROM builder AS tests
ARG BUILD_DATE
ARG VERSION

LABEL distro="tests"
LABEL org.opencontainers.image.created="$BUILD_DATE"
LABEL org.opencontainers.image.version="$VERSION"

ENV PATH=/app/.venv/bin:/usr/local/bin/:/usr/bin:/bin \
    DJANGO_SETTINGS_MODULE=bitcaster.config.settings \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=""\
    UWSGI_PROCESSES=4
WORKDIR /app
COPY uv.lock README.md MANIFEST.in pyproject.toml /app/
COPY src /app/src/

RUN --mount=type=cache,target=/root/.uv-cache \
    uv sync --cache-dir=/root/.uv-cache \
        --python=/usr/local/bin/python \
        --python-preference=system \
        --frozen



# ------- production only deps-------
FROM builder AS production
ENV PATH=/app/.venv/bin:/usr/local/bin/:/usr/bin:/bin \
    DJANGO_SETTINGS_MODULE=bitcaster.config.settings \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=""\
    UWSGI_PROCESSES=4
WORKDIR /app
COPY uv.lock README.md MANIFEST.in pyproject.toml /app/
COPY src /app/src/

RUN --mount=type=cache,target=/root/.uv-cache \
    uv sync --cache-dir=/root/.uv-cache \
        --python=/usr/local/bin/python \
        --python-preference=system \
        --no-dev --no-editable --frozen


# ------- dist -------
FROM base_os AS dist
ARG BUILD_DATE
ARG VERSION
ARG GIT_SHA

ENV PATH=/app/.venv/bin:/usr/local/bin/:/usr/bin:/bin \
    DJANGO_SETTINGS_MODULE=bitcaster.config.settings \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STATIC_URL="/static/" \
    PYTHONPATH=""\
    PGSSLCERT="/tmp/postgresql.crt" \
    UWSGI_PROCESSES=4

RUN <<EOF cat> /RELEASE
{"version": "$VERSION",
 "commit": "$GIT_SHA",
 "date": "$BUILD_DATE",
}
EOF
WORKDIR /app
COPY docker/conf /conf/
COPY docker/bin/* /usr/local/bin/
COPY LICENSE.md README.md /
COPY src /app/src/
RUN rm -fr /app/src/


COPY --chown=bitcatser:bitcatser-io --from=production /app/.venv /app/.venv
COPY --from=builder /usr/local/bin/uwsgi /usr/local/bin/uv /usr/local/bin/
RUN --mount=type=cache,target=/root/.uv-cache \
    --mount=type=bind,source=uv.lock,target=/app/uv.lock \
    --mount=type=bind,source=pyproject.toml,target=/app/pyproject.toml \
    --mount=type=bind,source=MANIFEST.in,target=/app/MANIFEST.in \
    --mount=type=bind,source=README.md,target=/app/README.md \
    --mount=type=bind,source=./src/bitcaster,target=/app/src/bitcaster \
    uv --cache-dir=/root/.uv-cache pip install --no-deps .


EXPOSE 8000
ENTRYPOINT exec docker-entrypoint.sh "$0" "$@"
CMD ["run"]

LABEL distro="final"
LABEL maintainer="bitcaster@bitcaster.io"
LABEL cheksum="$CHECKSUM"

LABEL org.opencontainers.image.authors="bitcaster@bitcaster.io"
LABEL org.opencontainers.image.created="$BUILD_DATE"
LABEL org.opencontainers.image.description="Bitcaster"
LABEL org.opencontainers.image.documentation="${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}"
LABEL org.opencontainers.image.licenses="${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/blob/${SOURCE_COMMIT:-master}/LICENSE.md"
LABEL org.opencontainers.image.revision=$SOURCE_COMMIT
LABEL org.opencontainers.image.source="${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/tree/${SOURCE_COMMIT:-master}/"
LABEL org.opencontainers.image.title="Bitcaster"
LABEL org.opencontainers.image.version="$VERSION"
LABEL org.opencontainers.image.url="https://bitcaster.io/"
LABEL org.opencontainers.image.vendor="OS4D ltd"
