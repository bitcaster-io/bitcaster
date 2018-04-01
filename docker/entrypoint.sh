#!/bin/bash
set -ex

if [ ! -f /var/bitcaster/.bootstrapped ]; then
    echo $PWD
    bitcaster configure --no-input
    bitcaster check --wait-services --deploy --sleep 10
    bitcaster upgrade --no-input
    touch /var/bitcaster/.bootstrapped
    echo "done" && exit 0
fi
#bitcaster start web -l debug &
#bitcaster start workers -l debug &

exec "$@"
