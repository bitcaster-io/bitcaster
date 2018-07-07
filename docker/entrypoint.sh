#!/bin/bash
set -ex


if [ "$@" == "bitcaster" ];then
    pg-control start
    redis-server &
    if [ ! -f /var/bitcaster/.bootstrapped ]; then
        touch /var/bitcaster/.bootstrapped
        bitcaster configure --no-input
        bitcaster upgrade --no-input
        echo "done"
    fi
    bitcaster start workers -l debug &
    exec bitcaster start web -l debug --bind 0.0.0.0:8000
else
    exec "$@"
fi
