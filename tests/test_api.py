import unittest
from requests import put, post
import json

API_BASE_URL = "http://ldap-srv:5000"


class TestLDAPI(unittest.TestCase):
    def test_connect_ldapi(self):

        resp = put(
            f"{API_BASE_URL}/hlo",
            data=json.dumps({"who": "cn=admin,cn=config", "secret": "bonjour"}),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "MyApp/1.0",
            },
        ).json()

        self.assertIsNotNone(resp)
        self.assertDictEqual(resp, {"status": "ok"})

    def test_create_db(self):

        resp = post(
            f"{API_BASE_URL}/db",
            data=json.dumps(
                {
                    "who": "cn=admin,cn=config",
                    "secret": "bonjour",
                    "suffix": "dc=gloubi,dc=org",
                    "rootpw": "whoami",
                    "directory": "/var/lib/ldap/databases/nested",
                }
            ),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "MyApp/1.0",
            },
        ).json()

        self.assertIsNotNone(resp)
        self.assertDictContainsSubset({"status": "ok"}, resp)

    def test_create_people_orgunit(self):
        resp = post(
            f"{API_BASE_URL}/ldif",
            data=json.dumps(
                {
                    "who": "cn=admin,cn=config",
                    "secret": "bonjour",
                    "new_dn": "ou=people,dc=gloubi,dc=org",
                    "new_data": {"objectClass": "organizationalUnit", "ou": "people"},
                }
            ),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "MyApp/1.0",
            },
        ).json()

        self.assertIsNotNone(resp)
        self.assertDictContainsSubset({"status": "ok"}, resp)

    def test_create_groups_orgunit(self):
        resp = post(
            f"{API_BASE_URL}/ldif",
            data=json.dumps(
                {
                    "who": "cn=admin,cn=config",
                    "secret": "bonjour",
                    "new_dn": "ou=groups,dc=gloubi,dc=org",
                    "new_data": {"objectClass": "organizationalUnit", "ou": "groups"},
                }
            ),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "MyApp/1.0",
            },
        ).json()

        self.assertIsNotNone(resp)
        self.assertDictContainsSubset({"status": "ok"}, resp)
