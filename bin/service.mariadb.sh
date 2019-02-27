#!/bin/bash -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )

if [[ -z "$1" ]]; then
    echo "usage $0 [start]"
    exit 1
fi

export LD_LIBRARY_PATH=${DIR}/mariadb/lib

case $1 in
start)
    export MYSQL_HOME=$SNAP_COMMON/config
    exec ${DIR}/mariadb/bin/mysqld --basedir=$SNAP/mariadb --datadir=$SNAP_COMMON/database --plugin-dir=$SNAP/mariadb/lib/plugin --pid-file=$SNAP_COMMON/database/mariadb.pid
    ;;

*)
    echo "not valid command"
    exit 1
    ;;
esac