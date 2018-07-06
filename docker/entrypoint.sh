#!/bin/sh
set -ex

if [ ! -f /var/bitcaster/.bootstrapped ]; then
    touch /var/bitcaster/.bootstrapped
    echo "done"
fi
if [ "$@" == "bitcaster" ];then
    pg-control start
    redis-server &
    bitcaster configure --no-input
    bitcaster upgrade --no-input
    bitcaster start web -l debug --bind 0.0.0.0:8000 &
    bitcaster start workers -l debug &
else
    exec "$@"
fi
