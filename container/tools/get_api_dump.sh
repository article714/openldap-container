#!/bin/bash

#set -x

curl http://ldap-srv:5000/ldif -v -X GET -H "Content-Type: application/json" -H "Accept: application/json, text/plain" -d "{'who':'cn=admin,cn=config','secret':'bonjour','dn': $1}" -o $2
