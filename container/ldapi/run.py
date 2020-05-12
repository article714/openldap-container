import json
import logging
import logging.config
from grp import getgrnam
from os import setgid, setuid
from pwd import getpwnam

from gevent.pywsgi import LoggingLogAdapter, WSGIServer

from ldapi import app

# ldapi configuration
ldapi_config = {}
with open("/container/config/ldapi-config.json", "r") as config:
    ldapi_config = json.load(config)


# setup logs
logconf = {}
with open("/container/config/ldapi-logging.json", "r") as config:
    logconf = json.load(config)

# secure process => no root!
gid = getgrnam(ldapi_config["group"]).gr_gid
uid = getpwnam(ldapi_config["user"]).pw_uid
setgid(gid)
setuid(uid)


logging.config.dictConfig(logconf)
log_adapter = LoggingLogAdapter(logging.getLogger("access"))
errorlog_adapter = LoggingLogAdapter(logging.getLogger("error"))

# start WSGI
http_server = WSGIServer(("", 5000), app, log=log_adapter, error_log=errorlog_adapter)
http_server.serve_forever()
