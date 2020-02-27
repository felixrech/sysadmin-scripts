import sys
sys.path.append(sys.path[0] + '/../99_helpers/')
from test_helpers import get_process_output, exists_mount  # noqa # pylint: disable=import-error
from test_helpers import set_log_length, print_log, print_check  # noqa # pylint: disable=import-error
from test_helpers import print_test_summary  # noqa # pylint: disable=import-error


print_log("Checking accessing a file on fileserver")
secret = get_process_output("su -c \"cat /home/rech/.fileserver_test\" rech")
print_check('my_secret' in secret)

print_log("Checking (auto)mount entry in df")
src = '192.168.10.6:/mnt/fileserver-pool/home/rech'
dst = '/home/rech'
print_check(exists_mount(src, dst))

print_test_summary()
