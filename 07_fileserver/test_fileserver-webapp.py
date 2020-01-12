import sys
sys.path.append(sys.path[0] + '/../99_helpers/')
from test_helpers import exists_mount  # noqa # pylint: disable=import-error
from test_helpers import set_log_length, print_log, print_check  # noqa # pylint: disable=import-error
from test_helpers import print_test_summary  # noqa # pylint: disable=import-error

# Set the test_log length to 50 chars
set_log_length(50)

src = '192.168.10.6:/mnt/fileserver-pool/services/webapp/status-monitor'
dst = '/mnt/status-monitor'

print_log("Checking mount for webapp")
print_check(exists_mount(src, dst))

print_test_summary()