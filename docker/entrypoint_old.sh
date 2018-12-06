#!/bin/bash
set -ex


if [ "$@" == "bitcaster" ];then
    pg-control start
    redis-server &
    if [ ! -f /var/bitcaster/.bootstrapped ]; then
        export BITCASTER_ORGANIZATION=`perl -e 'srand; rand($.) < 1 && ($line = $_) while <>; print $line;' /marvel.txt`

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
