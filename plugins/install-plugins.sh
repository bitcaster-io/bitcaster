#!/usr/bin/env sh
if [[ "$1" == "" ]]; then
    plugin_dir="$(CDPATH= cd -- "$( dirname -- "$0" )" && pwd -P)"
else
    plugin_dir=$1
fi

echo "Plugin dir: $plugin_dir"


for dir in `ls -d $plugin_dir/bitcaster-*`; do
    pip install $dir
done
