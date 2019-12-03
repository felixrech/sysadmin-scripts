#!/usr/bin/env python3.7

import os
import re
import sys
sys.path.append(sys.path[0] + '/../99_helpers/')
from test_helpers import filter_list_by_regex, get_page  # noqa # pylint: disable=import-error
from test_helpers import print_log, print_check, print_crit_check  # noqa # pylint: disable=import-error
from test_helpers import get_process_returncode, get_process_output  # noqa # pylint: disable=import-error
from test_helpers import print_test_summary  # noqa # pylint: disable=import-error


# One of the hostnames
main_hostname = 'psa-team10.in.tum.de'

# Logging
access_log_path = '/var/log/nginx/'
access_log_name = 'access.log'
error_log_path = '/var/log/nginx/'
error_log_name = 'error.log'


def get_logs(path, name, filter_ips=False):
    """ Opens all the log files in specified path with specified name and
        returns their content as a list containing all lines.

        When filter_ips is true, a regex is used to extract lines containing
        IP addresses.
    """
    files = os.listdir(path)
    log_pattern = r'^(' + re.escape(name) + r'(\.(\d)+)?)$'
    logs = filter_list_by_regex(files, log_pattern, group=1)
    logs = [(path + file) for file in logs]
    lines = []
    for log in logs:
        with open(log, 'r') as log_file:
            lines += log_file.readlines()
    if filter_ips:
        ip_pattern = r'((\d?\d?\d\.){3}\d?\d?\d)'
        lines = filter_list_by_regex(lines, ip_pattern, group=1)
    return logs, lines


# First, check whether nginx is even active
print_log("Checking nginx active")
cmd = "systemctl is-active --quiet nginx.service"
print_crit_check(get_process_returncode(cmd) == 0)

# Checking logfiles
print_log("Checking IPs in access log")
_, access_logs = get_logs(access_log_path, access_log_name, filter_ips=True)
print_check(len(access_logs) == 0)
print_log("Checking IPs in error log")
# Generating error to make sure error log isn't empty
get_page(main_hostname + '/idontexist.filetype')
_, error_logs = get_logs(error_log_path, error_log_name, filter_ips=True)
print_check(len(error_logs) > 0)

# Check logrotate
access_files, access_logs = get_logs(access_log_path, access_log_name)
error_files, error_logs = get_logs(error_log_path, error_log_name)
print_log("Checking whether logrotate is active")
print_check(len(access_files) == 2 and len(error_files) == 6)


print_test_summary()
