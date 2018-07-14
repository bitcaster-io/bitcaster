#!/usr/bin/env bash

if [ "$1" == "" ]; then
    PLUGIN_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
else
    PLUGIN_DIR=$1
fi

echo "Plugin dir: $PLUGIN_DIR"


for dir in `ls -d $PLUGIN_DIR/bitcaster-*`; do
    pip install $dir
done
