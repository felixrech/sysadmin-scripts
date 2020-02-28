import sys

sys.path.append(sys.path[0] + '/../99_helpers/')
from test_helpers import read_config  # noqa # pylint: disable=import-error
from test_helpers import get_process_returncode, get_page, run_remote_test  # noqa # pylint: disable=import-error
from test_helpers import print_log, print_check  # noqa # pylint: disable=import-error
from test_helpers import print_test_summary  # noqa # pylint: disable=import-error


secret = "<title>Nagios: nagios.psa-team10.in.tum.de</title>"
auth = (read_config('nagios-username'),
        read_config('nagios-password'))


print_log("Checking server active")
rc = get_process_returncode("systemctl is-active --quiet nagios")
print_check(rc == 0)

print_log("Checking server available")
page = get_page('nagios.psa-team10.in.tum.de/nagios/', auth=auth)
print_check(secret in page)

run_remote_test('vm01', 'nagios-available')

print_test_summary()
