import hashlib
from base64 import urlsafe_b64encode as encode
from os import urandom

import ldap

from flask import request


GOOD_RESULT = {"status": "ok"}


def decode_json(needed_entries, auth_needed=True):
    """
    decode Json from request
    """
    try:
        valid = True
        json_data = request.get_json(force=True)
        if auth_needed:
            valid = ("who" in json_data) and ("secret" in json_data)
        for val in needed_entries:
            valid = valid and (val in json_data)
        if valid:
            return json_data
        return None
    except Exception:
        return None


def encode_to_bs(data):
    """
    encode values of a dictionnary to utf-8 bytestrings
    """

    if isinstance(data, dict):
        for key in data:
            if isinstance(data[key], str):
                try:
                    data[key] = data[key].encode("utf-8")
                except UnicodeEncodeError:
                    return False
            elif isinstance(data[key], list):
                try:
                    data[key] = [x.encode("utf-8") for x in data[key]]
                except UnicodeEncodeError:
                    return False

        return True
    return False


def makeSSHASecret(secret):
    """
    Encode Password (LDAP format)
    """
    salt = urandom(4)
    h = hashlib.sha1(secret.encode("utf-8"))
    h.update(salt)
    return "{{SSHA}}{}".format(encode(h.digest() + salt).decode("utf-8"))


def _connect(json_data):
    """
    Common connect method
    """

    ldap_o = ldap.initialize("ldapi:///")
    try:
        ldap_o.simple_bind_s(who=json_data["who"], cred=json_data["secret"])
    except Exception:
        return None
    return ldap_o
