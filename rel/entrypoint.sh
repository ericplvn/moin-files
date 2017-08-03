#!/bin/bash

set -e

export PATH="/usr/bin:$PATH"
export PYTHONPATH=/srv/wiki-common/config

# Scope AWS secrets to just the mail setup process. Nothing else in the
# environment needs them and we don't want something to accidentally leak them
# outside in a stack trace or a debug dump
#(
#    source /srv/wiki/aws/secrets.sh
#    configure_ssmtp.sh
#)

if [[ -z "$WIKIUID" ]]; then
    echo "No WIKIUID environment variable"
    exit 1
fi

if [[ -z "$WIKIGID" ]]; then
    WIKIGID=$WIKIUID
fi

groupmod -g $WIKIGID wiki
usermod -u $WIKIUID -g $WIKIGID wiki

if [[ ! -d "/srv/wiki/data/cache/xapian/index" ]]; then
    su-exec wiki:wiki moin --config-dir /srv/wiki/config index build --mode=rebuild
fi

exec "$@"
