#!/bin/bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )

if [[ -z "$1" ]]; then
    echo "usage $0 [start]"
    exit 1
fi

. ${DIR}/config/environment

case $1 in
start)
    exec $DIR/bin/snandardfile -db ${SNAP_DATA}/database.sqlite -p ${STANDARD_PORT} -foreground
    ;;
*)
    echo "not valid command"
    exit 1
    ;;
esac
