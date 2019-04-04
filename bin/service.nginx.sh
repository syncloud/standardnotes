#!/bin/bash -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )

if [[ -z "$1" ]]; then
    echo "usage $0 [start|stop]"
    exit 1
fi

SOCKET=${SNAP_DATA}/notes.socket

case $1 in
pre-start)
    timeout 600 /bin/bash -c 'until [ -S '${SOCKET}' ]; do echo "waiting for ${SOCKET}"; sleep 1; done'
    /bin/rm -f ${SNAP_COMMON}/web.socket
    exec ${DIR}/nginx/sbin/nginx -t -c ${SNAP_DATA}/config/nginx.conf -p ${DIR}/nginx -g 'error_log '${SNAP_COMMON}'/log/nginx_error.log warn;'
    ;;
start)
    exec ${DIR}/nginx/sbin/nginx -c ${SNAP_DATA}/config/nginx.conf -p ${DIR}/nginx -g 'error_log '${SNAP_COMMON}'/log/nginx_error.log warn;'
    ;;
reload)
    ${DIR}/nginx/sbin/nginx -c ${SNAP_DATA}/config/nginx.conf -s reload -p ${DIR}/nginx
    ;;
stop)
    ${DIR}/nginx/sbin/nginx -c ${SNAP_DATA}/config/nginx.conf -s stop -p ${DIR}/nginx
    ;;
*)
    echo "not valid command"
    exit 1
    ;;
esac
