import sys
import logging

import ldap

CONFIG_DB_DN = "olcDatabase={0}config,cn=config"

# ---------------------------------
# Go main
if __name__ == "__main__":
    encrypted_pwd = None
    delay = 2
    retry_count = 0

    if len(sys.argv) < 3:
        print("Usage: dump_ldif.py <baseDN> <filename>")
        sys.exit(-1)
    else:
        baseDN = sys.argv[1]
        fileName = sys.argv[2]

    ldap_o = ldap.initialize("ldapi:///")

    with open(fileName, "w") as ldif_output:

        s = ldap.asyncsearch.LDIFWriter(ldap_o, ldif_output)

        s.startSearch(baseDN, ldap.SCOPE_SUBTREE, "(objectClass=*)")

        try:
            partial = s.processResults()
        except ldap.SIZELIMIT_EXCEEDED:
            logging.error("Warning: Server-side size limit exceeded.\n")
        else:
            if partial:
                logging.error("Warning: Only partial results received.\n")

        logging.error(
            "%d results received.\n", s.endResultBreak - s.beginResultsDropped
        )

    ldap_o.unbind()
