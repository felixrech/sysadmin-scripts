import os
import sys
sys.path.append(sys.path[0] + '/../99_helpers/')
from test_helpers import print_log, print_check, print_crit_check  # noqa # pylint: disable=import-error
from test_helpers import get_process_output  # noqa # pylint: disable=import-error

# Configure the LDAP server used
ldap_host = "ldaps://ldap.psa-team10.in.tum.de"
ldap_base_dn = "dc=team10,dc=psa,dc=in,dc=tum,dc=de"
ldap_binddn = "uid=root1,ou=Students," + ldap_base_dn
# Construct a base ldapsearch string
base = "ldapsearch -H {0} -D \"{1}\" -w \"test1\" "
ldap_search_base = base.format(ldap_host, ldap_binddn)

# Set the test_log length to 50 chars
log_length = 50


def check_login(password="test1", tls=True):
    # If tls=False use ldap://ldap.psa-team10.in.tum.de instead of ldap_host
    host = ldap_host if tls else ldap_host.replace('ldaps', 'ldap')
    # Use a ldapwhoami to check whether login w/ given pw possible (use timeout)
    cmd = "ldapwhoami -H {0} -D {1} -o nettimeout=5 -w \"{2}\""
    cmd = cmd.format(host, ldap_binddn, password)
    return ldap_binddn in get_process_output(cmd)


def get_uids(in_oud):
    # Get all the uids, limit output to actual uids, then return them as tuple
    cmd = ldap_search_base + \
        "-b \"ou={0},{1}\" uid=* uid ".format(in_oud, ldap_base_dn) + \
        "| grep -a \"uid: \" | cut -d ' ' -f 2"
    return get_process_output(cmd).splitlines()


def get_user_attributes(attributes):
    # Get given attributes of the root1 user using ldapsearch
    cmd = ldap_search_base + \
        "-b \"{0}\" -LLL {1}".format(ldap_binddn, ' '.join(attributes))
    return get_process_output(cmd).splitlines()[1:-1]


def checking_encrypted_communication():
    # Check whether we can log in using TLS
    print_log("Checking login/whoami using TLS", fill=log_length)
    print_crit_check(check_login())
    # Check whether we can log in w/o TLS
    print_log("Checking login/whoami w/o TLS not allowed", fill=log_length)
    print_check(not check_login(tls=False))


def check_organizational_units():
    # Get all the organizational units from the LDAP server
    cmd = ldap_search_base + \
        "-LLL objectClass=organizationalUnit | grep dn: | cut -d ' ' -f2"
    ous = get_process_output(cmd).split('\n')
    # Check that both the 'Praktikum' and 'Students' organizational units exist
    if ((not any(ou for ou in ous if ou.startswith('ou=Praktikum'))) or
            (not any(ou for ou in ous if ou.startswith('ou=Students')))):
        return False
    # Check that the team sub-organizational units exist
    for i in range(1, 12):
        if not any(ou for ou in ous if ou.startswith('ou=Team{},ou=Praktikum'.format(i))):
            return False
    # If we're here, all required organizational units exist
    return True


def check_existing_users():
    # Check that the number of user in the Praktikum ou is correct
    return len(get_uids('Praktikum')) == 24


def check_csv_users():
    # Check that the number of user in the Students ou is correct
    return len(get_uids('Students')) == 87


def check_csv_attributes():
    # Check whether attributes in inetOrgPerson, student, posixAccount
    # classes are set correctly
    attr = ["objectClass", "sn", "matrNr", "telephoneNumber", "gidNumber"]
    attr = get_user_attributes(attr)
    return ("objectClass: student" in attr and
            "objectClass: posixAccount" in attr and
            "objectClass: shadowAccount" in attr and
            "matrNr: 1938351754" in attr and
            "sn: Root" in attr and
            "telephoneNumber: 03530-68758152" in attr and
            "gidNumber: 2000" in attr)


def check_csv_certificate():
    # Extract certificate from LDAP
    cert = get_user_attributes(['userCertificate'])
    if len(cert) < 2:
        return False
    # Remove "userCertificate;binary: " and add start/end delimiters
    start = "-----BEGIN CERTIFICATE-----"
    cert = '\n'.join([cert[0][25:]] + cert[1:])
    end = "-----END CERTIFICATE-----"
    # Write the certificate to a temporary file
    with open('test.der', 'w') as f:
        f.write('\n'.join([start, cert, end]) + '\n')
    # Get certificate content using openssl
    cmd = "openssl x509 -noout -text -in test.der"
    openssl_out = get_process_output(cmd)
    # Delete the temporary file
    os.remove('test.der')
    # Check whether the subject is set correctly
    test_string = "Subject: C = DE, ST = Bavaria, L = Munich, O = PSA Team 10, OU = Students, CN = Olga Root, emailAddress = root1@students.psa-team10.in.tum.de"
    return test_string in openssl_out


def check_passwd():
    def change_pw(old_password, new_password):
        # Execute passwd as test1 user
        cmd = "runuser -l root1 -c \"echo \\\"{0}\\n{1}\\n{1}\\\" | passwd\" 2>&1"
        out = get_process_output(cmd.format(old_password, new_password))
        return "password updated successfully" in out

    # Try to use passwd
    print_log("Checking passwd works", fill=log_length)
    success = change_pw("test1", "test2")
    print_check(success)
    if not success:
        return

    # Try to log in using old, then new password
    print_log("Checking password changed", fill=log_length)
    success = not check_login("test1") and check_login("test2")
    print_check(success)

    # Reset password for next test run
    change_pw("test2", "test1")


def check_anonymous_bind():
    # Use anonymous bind to try and get uid & matrNr, then only matrNr
    cmd = "ldapsearch -H {0} -x uid=root1 uid{1}"
    out1 = get_process_output(cmd.format(ldap_host, ", matrNr"))
    out2 = get_process_output(cmd.format(ldap_host, ''))
    # The 2nd command should have worked and the 1st not
    return "uid: root1" in out2 and not "matrNr: 1938351754" in out1


# Check encrypted communication w/ server
checking_encrypted_communication()
# Check organizational units
print_log("Checking organizational units", fill=log_length)
print_check(check_organizational_units())
# Check existing user
print_log("Checking Praktikum users exist", fill=log_length)
print_check(check_existing_users())
# Check csv user
print_log("Checking csv users exist", fill=log_length)
print_check(check_csv_users())
# Check csv user details
print_log("Checking csv users attributes", fill=log_length)
print_check(check_csv_attributes())
# Check csv user certificate
print_log("Checking csv users have certificate", fill=log_length)
print_check(check_csv_certificate())
# Check passwd
check_passwd()
# Check anonymous bind permissions
print_log("Checking anonymous bind permissions", fill=log_length)
print_check(check_anonymous_bind())
