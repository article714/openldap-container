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
    if [[ ! -f "/container/config/slapd/certs/slapd.crt" && -n "${LDAP_X509_SUBJECT}" ]]; then
        # Build self-signed Certificate
        chown slapd.root /container/config/slapd/certs
        cd /container/config/slapd/certs
        if [ -n "${LDAP_X509_ALTNAMES}" ]; then
            chpst -u openldap openssl req -newkey rsa:4096 -days 1001 -nodes -x509 -subj ${LDAP_X509_SUBJECT} -addext "subjectAltName=${LDAP_X509_ALTNAMES}" -keyout "slapd.key" -out "slapd.crt"
        else
            chpst -u openldap openssl req -newkey rsa:4096 -days 1001 -nodes -x509 -subj ${LDAP_X509_SUBJECT} -keyout "slapd.key" -out "slapd.crt"
        fi

    fi

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
