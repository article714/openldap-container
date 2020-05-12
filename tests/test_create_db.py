import logging
import unittest

import ldap
from ldap import modlist

TESTING_DB_SUFFIX = "dc=lease4,dc=net"


class TestCreateDb(unittest.TestCase):
    """
    Test creating a new Databsase
    """

    def _connect(self):
        ldap_o = ldap.initialize("ldap://ldap-srv/")
        self.assertIsNotNone(ldap_o)
        try:
            ldap_o.simple_bind_s(who="cn=admin,cn=config", cred="bonjour")
        except Exception as e:
            logging.exception("FAILED TO BIND")
            self.fail("FAILED TO BIND: %s" % str(e))
        return ldap_o

    def test_connect_ldapi(self):
        ldap_o = self._connect()
        self.assertIsNotNone(ldap_o)

    def test_create_db(self):
        modifs = modlist.addModlist(
            {
                "objectClass": [b"olcDatabaseConfig", b"olcMdbConfig"],
                "olcDatabase": [b"mdb"],
                "OlcDbMaxSize": [b"1073741824"],
                "olcSuffix": [TESTING_DB_SUFFIX.encode("utf-8")],
                "olcRootDN": [f"cn=admin,{TESTING_DB_SUFFIX}".encode("utf-8")],
                "olcRootPW": [b"secret"],
                "olcDbDirectory": [b"/var/lib/ldap/databases/"],
                "olcDbIndex": [b"objectClass eq"],
            }
        )

        ldap_o = self._connect()
        self.assertIsNotNone(ldap_o)

        ldap_o.add_s("olcDatabase=mdb,cn=config", modifs)

    def test_retreive_db(self):

        ldap_o = self._connect()
        self.assertIsNotNone(ldap_o)

        result = ldap_o.search_s(
            "cn=config",
            ldap.SCOPE_SUBTREE,
            f"(&(objectClass=olcDatabaseConfig)(olcSuffix={TESTING_DB_SUFFIX}))",
        )
        found = False
        for obj in result:
            if obj[1]["olcSuffix"][0].decode("utf-8") == TESTING_DB_SUFFIX:
                found = True

        self.assertEqual(len(result), 1)

        self.assertTrue(found)
