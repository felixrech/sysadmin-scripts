import sys
import tempfile
from smb.SMBConnection import SMBConnection
sys.path.append(sys.path[0] + '/../99_helpers/')
from test_helpers import read_config  # noqa # pylint: disable=import-error
from test_helpers import print_log, print_check, print_crit_check  # noqa # pylint: disable=import-error
from test_helpers import print_test_summary  # noqa # pylint: disable=import-error


# Read password from configuration file
password = read_config('samba-rech-password')


print_log("Checking samba server reachable")
con = SMBConnection("rech", password, "local_name", "local_machine")
try:
    con.connect("192.168.10.6", 445)
except Exception:
    con = None
print_crit_check(con is not None)

print_log("Checking home shared over samba")
shares = list(map(lambda x: x.name, con.listShares()))
print_crit_check('rech' in shares)

print_log("Checking files listed in samba")
files = map(lambda x: x.filename, con.listPath('rech', '/'))
print_check('.fileserver_test' in files)

print_log("Checking file read over samba")
f = tempfile.NamedTemporaryFile()
con.retrieveFile('rech', '/.fileserver_test', f)
f.seek(0)   # pysmb starts at end of file
print_check('my_secret' in f.read().decode('utf-8'))

print_test_summary()
