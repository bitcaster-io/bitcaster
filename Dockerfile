FROM python:3.6
ENV PYTHONUNBUFFERED 1

RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ jessie-pgdg main' $PG_MAJOR > /etc/apt/sources.list.d/pgdg.list \
    && apt-get update && apt-get install -y --no-install-recommends \
        postgresql-common \
        postgresql-$PG_MAJOR=$PG_VERSION \
        postgresql-client-$PG_MAJOR=$PG_VERSION \
        postgresql-contrib-$PG_MAJOR=$PG_VERSION \
    && rm -rf /var/lib/apt/lists/* \
    && rm "/etc/postgresql/$PG_MAJOR/main/pg_hba.conf" \
    && touch "/etc/postgresql/$PG_MAJOR/main/pg_hba.conf" \
    && chown -R postgres "/etc/postgresql/$PG_MAJOR/main/pg_hba.conf" \
    && { echo; echo "host all all 0.0.0.0/0 trust"; } >> "/etc/postgresql/$PG_MAJOR/main/pg_hba.conf" \
    &&  { echo; echo "local all all trust"; } >> "/etc/postgresql/$PG_MAJOR/main/pg_hba.conf"

RUN service postgresql start \
    && createdb -U postgres -E utf-8 --template template0 sentry \
    && service postgresql stop

RUN mkdir /code
WORKDIR /code
ADD src/requirements/install.pip /code/
RUN pip install -r install.pip
ADD . /code/
