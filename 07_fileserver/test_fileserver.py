import os
import sys
sys.path.append(sys.path[0] + '/../99_helpers/')
from test_helpers import get_process_output, run_remote_test  # noqa # pylint: disable=import-error
from test_helpers import set_log_length, print_log, print_check, print_crit_check  # noqa # pylint: disable=import-error
from test_helpers import print_test_summary  # noqa # pylint: disable=import-error

# Set the test_log length to 50 chars
set_log_length(50)

def check_hdds_size():
    def get_block_device_size(dev):
        # Get block device size in bytes
        out = get_process_output("lsblk -brno SIZE /dev/{}".format(dev))
        # Convert from bytes to GiB
        return int(out.splitlines()[0]) / (2**30)
    # Get all block devices in fileserver-pool
    out = get_process_output("zpool status -L fileserver-pool")
    out = out[out.find('config:'):out.find('errors:')]
    devs = [l[5:8] for l in out.splitlines() if l.startswith('\t    ')]
    # Check whether we have the right number of them
    print_log("Checking correct number of block devices")
    print_check(len(devs) == 7)
    # Check whether no block device is larger than 2GiB
    print_log("Checking block devices sizes")
    print_check(all(map(lambda x: x<=2, map(get_block_device_size, devs))))

def check_fileserver_size_mount():
    # Get output of df -h and extract fileserver-pool line
    df = get_process_output("df -h").splitlines()
    lines = [l for l in df if l.startswith("fileserver-pool        12G")]
    # Check whether df -h contains fileserver-pool line
    print_log("Checking df -h combined size")
    print_check(len(lines) > 0)
    # Check whether fileserver-pool line mentions a mount at /mnt/fileserver-pool
    print_log("Checking pool mounted")
    print_crit_check(len(lines) > 0  and lines[0].endswith('/mnt/fileserver-pool'))

def check_remote_mounts():
    run_remote_test('vm1', 'fileserver-website')
    run_remote_test('vm3', 'fileserver-database-master')
    run_remote_test('vm4', 'fileserver-database-slave')
    run_remote_test('vm5', 'fileserver-webapp')

check_hdds_size()
check_fileserver_size_mount()
check_remote_mounts()
print_test_summary()