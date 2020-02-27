import sys

sys.path.append(sys.path[0] + '/../99_helpers/')
from test_helpers import get_page, get_process_returncode, Cursor  # noqa # pylint: disable=import-error
from test_helpers import print_log, print_check, run_remote_test  # noqa # pylint: disable=import-error
from test_helpers import print_test_summary  # noqa # pylint: disable=import-error

print_log("Checking testrunner active")
rc = get_process_returncode("systemctl is-active --quiet dash-testrunner")
print_check(rc == 0)

print_log("Checking server active")
rc = get_process_returncode("systemctl is-active --quiet dash-server")
print_check(rc == 0)

print_log("Checking nginx proxy active")
rc = get_process_returncode("systemctl is-active --quiet nginx")
print_check(rc == 0)

print_log("Checking website online")
page = get_page('localhost')
print_check("<title>Status app</title>" in page)

print_log("Checking all tests executed")
with Cursor() as c:
    sql = ('''select test, vm from run_on where not exists '''
           '''( select * from test_results '''
           '''where test_results.test = run_on.test '''
           '''and test_results.vm = run_on.vm );''')
    c.execute(sql)
    print_check(len(c.fetchall()) == 0)

run_remote_test('vm01', 'webapp-available')

print_test_summary()
