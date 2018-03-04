#!/bin/bash
set -ex

# Make sure to always start all the background services
service postgresql start
service redis-server start
service memcached start
service postfix start
service ntp start

if [ ! -f /.bootstrapped ]; then
    echo $PWD
    pip install -e .[dev]
    bitcaster upgrade
    bitcaster configure --noinput
    touch /.bootstrapped
    echo "done" && exit 0
fi

exec "$@"
