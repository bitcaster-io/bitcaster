#!/bin/bash
set -ex

# Make sure to always start all the background services
service postgresql start
service redis-server start
#service postfix start
#service ntp start

if [ ! -f /var/bitcaster/.bootstrapped ]; then
    echo $PWD
    export BITCASTER_ORGANIZATION=`perl -e 'srand; rand($.) < 1 && ($line = $_) while <>; print $line;' /marvel.txt`

    pip install "pip<10"
    pip install -e .[dev]
    bitcaster configure --no-input
    bitcaster upgrade --no-input
    touch /var/bitcaster/.bootstrapped
    echo "done" && exit 0
fi
#bitcaster start web -l debug &
#bitcaster start workers -l debug &

exec "$@"
