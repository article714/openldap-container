#!/bin/bash

apt-get update
apt-get upgrade -yq
apt-get install -y locales
localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
localedef -i fr_FR -c -f UTF-8 -A /usr/share/locale/locale.alias fr_FR.UTF-8

export LANG=en_US.utf8

# Install needed python-dev packages
LC_ALL=C DEBIAN_FRONTEND=noninteractive apt-get install -qy --no-install-recommends runit rsyslog logrotate \
    curl \
    slapd slapd-contrib \
    python3-ldap python3-flask-restful python3-requests python3-gevent ldap-utils

# Add Syslog user
groupadd -g 110 syslog
adduser --no-create-home --disabled-password --shell /usr/sbin/nologin --gecos "" --uid 104 --gid 110 syslog

chgrp syslog /var/log
chmod 775 /var/log

#--
# config files redirection

rm -f /etc/rsyslog.conf
ln -s /container/config/rsyslog.conf /etc/rsyslog.conf

rm -f /etc/logrotate.conf
ln -s /container/config/logrotate.conf /etc/logrotate.conf

rm -rf /etc/crontab /etc/cron.d
ln -s /container/config/crontab /etc/crontab
ln -s /container/config/cron.d /etc/cron.d

#--
# Cleaning
apt-get -yq clean
apt-get -yq autoremove
rm -rf /var/lib/apt/lists/*
# remove default Ldap DB
rm -rf /var/lib/ldap /etc/ldap/slapd.d
# cleanup useless cron jobs
rm -f /etc/cron.daily/passwd /etc/cron.daily/dpkg /etc/cron.daily/apt-compat
# truncate logs
truncate --size 0 /var/log/lastlog
truncate --size 0 /var/log/faillog
truncate --size 0 /var/log/dpkg.log
truncate --size 0 /var/log/syslog
