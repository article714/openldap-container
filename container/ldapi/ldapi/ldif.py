import logging
import tempfile
from os import unlink

from ldap import SCOPE_SUBTREE, SIZELIMIT_EXCEEDED, asyncsearch, modlist

from flask import send_file
from flask_restful import Resource

from .utils import GOOD_RESULT, _connect, decode_json, encode_to_bs


class LdifEndpoint(Resource):
    """
    Apply Some LDIF instructions
    """

    def get(self,):
        """
        gets an ldif file
        """

        json_data = decode_json(["dn"])
        if json_data is None:
            return {"status": "failed", "reason": "Wrong input data"}

        ldap_o = _connect(json_data)

        if ldap_o is not None:

            try:
                tmpfile = tempfile.NamedTemporaryFile(delete=False)

                with open(tmpfile, "w") as ldif_output:
                    s = asyncsearch.LDIFWriter(ldap_o, ldif_output)

                    s.startSearch(json_data["dn"], SCOPE_SUBTREE, "(objectClass=*)")

                    try:
                        partial = s.processResults()
                    except SIZELIMIT_EXCEEDED:
                        logging.error("Warning: Server-side size limit exceeded.\n")
                    else:
                        if partial:
                            logging.error(
                                "API: LDIF dump =>  Warning: Only partial results received.\n"
                            )

                    logging.error(
                        "API: LDIF dump => %d results received.\n",
                        s.endResultBreak - s.beginResultsDropped,
                    )

                ldap_o.unbind()
                return send_file(tmpfile.name, mimetype="text/plain;charset=utf-8")

                unlink(tmpfile.name)

            except Exception as e:
                return {"status": "failed", "reason": f"Exception raised {e}"}

            ldap_o.unbind()
        return {"status": "failed", "reason": "Cannot connect to LDAP"}

    def put(self,):
        """
        ldapmodify LDIF
        """

        json_data = decode_json(["orig_data", "mod_list", "dn"])
        if json_data is None:
            return {"status": "failed", "reason": "Wrong input data"}

        ldap_o = _connect(json_data)

        if ldap_o is not None:

            if isinstance(json_data["orig_data"], dict) and isinstance(
                json_data["mod_list"], dict
            ):
                if not encode_to_bs(json_data["orig_data"]):
                    return {
                        "status": "failed",
                        "reason": "Unable to decode input data (orig_data)",
                    }
                if not encode_to_bs(json_data["mod_list"]):
                    return {
                        "status": "failed",
                        "reason": "Unable to decode input data (mod_list)",
                    }
                try:
                    modifs = modlist.modifyModlist(
                        json_data["orig_data"], json_data["mod_list"]
                    )

                    ldap_o.modify_s(json_data["dn"], modifs)

                    ldap_o.unbind()
                    return GOOD_RESULT
                except Exception as e:
                    return {"status": "failed", "reason": f"Exception raised {e}"}

        return {"status": "failed", "reason": "Cannot connect to LDAP"}

    def post(self,):
        """
        ldapadd LDIF
        """

        json_data = decode_json(["new_data", "new_dn"])
        if json_data is None:
            return {"status": "failed", "reason": "Wrong input data"}

        ldap_o = _connect(json_data)

        if ldap_o is not None:

            if isinstance(json_data["new_data"], dict):

                if not encode_to_bs(json_data["new_data"]):
                    return {
                        "status": "failed",
                        "reason": "Unable to decode input data (new_data)",
                    }

                try:
                    modifs = modlist.addModlist(json_data["new_data"])

                    ldap_o.add_s(json_data["new_dn"], modifs)

                    ldap_o.unbind()
                    return GOOD_RESULT
                except Exception as e:
                    return {"status": "failed", "reason": f"Exception raised {e}"}

            return {"status": "failed", "reason": "Wrong input data format"}

        return {"status": "failed", "reason": "Cannot connect to LDAP"}
