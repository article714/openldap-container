#!/bin/bash

PATH=/sbin:/usr/sbin:/bin:/usr/bin

#set -x

update_pwd() {
    if [ "$1" != "" ]; then
        encrypted=$(slappasswd -h {SSHA} -s "$1")
        python3 /container/tools/set_admin_pwd.py ${encrypted} 3 &
    fi
}

start() {
    exec runsvdir -P /container/services
}

case "$1" in
initpwd)
    update_pwd "$2"
    start
    ;;
start)
    start
    ;;
shell)
    exec "/bin/bash"
    ;;
--)
    start
    ;;
*)
    exec "$@"
    ;;
esac

exit 1
