import sys
from time import sleep

import ldap
from ldap import modlist

CONFIG_DB_DN = "olcDatabase={0}config,cn=config"

# ---------------------------------
# Go main
if __name__ == "__main__":
    encrypted_pwd = None
    delay = 2
    retry_count = 0

    if len(sys.argv) < 2:
        print("Usage: set_admin_pwd.py <new_encrypted_pwd> <wait_delay>")
        sys.exit(-1)
    else:
        encrypted_pwd = sys.argv[1].encode("utf-8")
    if len(sys.argv) == 3:
        delay = int(sys.argv[2])

    ldap_o = ldap.initialize("ldapi:///")
    failed = True
    while retry_count < 3 and failed:
        try:
            # ldap_o.sasl_non_interactive_bind_s("EXTERNAL")
            ldap_o.sasl_external_bind_s()
            failed = False
        except ldap.SERVER_DOWN:
            print(f"ON VA REESSAYER {retry_count} ")
            retry_count += 1
            sleep(delay)

    result = ldap_o.search_s("cn=config", ldap.SCOPE_SUBTREE, f"dn={CONFIG_DB_DN}")

    init_pwd = True
    for obj in result:
        print(f"ON A TROUVE {obj[0]} --> {obj[1]}")
        if obj[0] == CONFIG_DB_DN:
            init_pwd = "olcRootPW" not in obj[1]

    if init_pwd:
        # init pwd
        modifs = modlist.modifyModlist(
            {}, {"olcRootPW": [encrypted_pwd]}, ignore_oldexistent=1
        )
    else:
        # replace pwd
        modifs = modlist.modifyModlist(
            {"olcRootPW": []}, {"olcRootPW": [encrypted_pwd]}, ignore_oldexistent=1
        )

    ldap_o.modify_s(CONFIG_DB_DN, modifs)

    ldap_o.unbind()
