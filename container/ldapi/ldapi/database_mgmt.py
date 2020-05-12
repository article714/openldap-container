import os
from os import path

import ldap
from ldap import modlist

from flask_restful import Resource

from .utils import _connect, makeSSHASecret, decode_json, GOOD_RESULT


class DatabaseMgmt(Resource):
    """
    Database Management
    """

    def post(self,):
        """
        Creates a new Database
        """

        json_data = decode_json(["suffix", "rootpw", "directory"])
        if json_data is None:
            return {"status": "failed", "reason": "Wrong input data"}

        suffix = json_data["suffix"]
        directory = json_data["directory"]
        dbsecret = makeSSHASecret(json_data["rootpw"])

        ldap_o = _connect(json_data)

        result = {}
        if ldap_o is not None:
            if not path.exists(directory):
                os.makedirs(directory)
                try:
                    self._create_db(ldap_o, suffix, directory, dbsecret)
                    dn = self._retreive_db(ldap_o, suffix)
                    self._create_org(ldap_o, suffix)
                except Exception as e:
                    return {"status": "failed", "reason": f"Exception raised {e}"}
                if dn is None:
                    result = {"status": "failed", "reason": "Database not found"}
                result.update(GOOD_RESULT)
                result["dn"] = dn
            else:
                result = {"status": "failed", "reason": "Directory already exists"}
            ldap_o.unbind()
            return result
        return {"status": "failed", "reason": "Cannot connect to LDAP"}

    def _create_db(self, ldap_o, suffix, directory, dbsecret):
        """
        Create the Database
        """
        modifs = modlist.addModlist(
            {
                "objectClass": [b"olcDatabaseConfig", b"olcMdbConfig"],
                "olcDatabase": [b"mdb"],
                "OlcDbMaxSize": [b"1073741824"],
                "olcSuffix": [suffix.encode("utf-8")],
                "olcRootDN": [f"cn=admin,{suffix}".encode("utf-8")],
                "olcRootPW": [dbsecret.encode("utf-8")],
                "olcDbDirectory": [f"{directory}".encode("utf-8")],
                "olcDbIndex": [b"objectClass eq"],
                "olcAccess": [
                    (
                        "to attrs=userPassword,shadowLastChange  by self write  "
                        "by anonymous auth  "
                        f'by dn="cn=admin,{suffix}" write by * none'
                    ).encode("utf-8"),
                    (
                        f'to dn.base="" by dn="cn=admin,{suffix}" manage '
                        'by dn="cn=admin,cn=config" manage '
                        "by dn.exact=gidNumber=0+uidNumber=0,cn=peercred,cn=external,cn=auth manage"
                        " by * read "
                    ).encode("utf-8"),
                    (
                        f'to * by self write by dn="cn=admin,{suffix}" manage '
                        'by dn="cn=admin,cn=config" manage '
                        "by dn.exact=gidNumber=0+uidNumber=0,cn=peercred,cn=external,cn=auth manage"
                        " by * read"
                    ).encode("utf-8"),
                ],
            }
        )

        ldap_o.add_s("olcDatabase=mdb,cn=config", modifs)

    def _create_org(self, ldap_o, suffix):
        """
        Create top Organization (first DN in database)
        """
        dcs = [x.split("=")[-1] for x in suffix.split(",")]

        orgname = ".".join(dcs).encode("utf-8")
        firstdc = dcs[0].encode("utf-8")

        modifs = modlist.addModlist(
            {
                "objectClass": [b"top", b"dcObject", b"organization"],
                "dc": firstdc,
                "o": orgname,
            }
        )

        ldap_o.add_s(suffix, modifs)

    def _retreive_db(self, ldap_o, suffix):
        """
        search for created Database
        """
        result = ldap_o.search_s(
            "cn=config",
            ldap.SCOPE_SUBTREE,
            f"(&(objectClass=olcDatabaseConfig)(olcSuffix={suffix}))",
        )
        dn = None
        for obj in result:
            if obj[1]["olcSuffix"][0].decode("utf-8") == suffix:
                dn = obj[0]

        return dn
