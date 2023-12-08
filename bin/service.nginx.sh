#!/bin/bash -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )

if [[ -z "$1" ]]; then
    echo "usage $0 [start|stop]"
    exit 1
fi

SOCKET=${SNAP_DATA}/standardnotes.socket
timeout 100 /bin/bash -c 'until [ -S '${SOCKET}' ]; do echo "waiting for '${SOCKET}'"; sleep 1; done'
/bin/rm -f ${SNAP_COMMON}/web.socket
/bin/rm -f ${SNAP_COMMON}/log/nginx*.log
exec ${DIR}/nginx/sbin/nginx -c ${SNAP_DATA}/config/nginx.conf -p ${DIR}/nginx -e stderr
