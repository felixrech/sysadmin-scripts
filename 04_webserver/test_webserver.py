#!/usr/bin/env python3.7

import os
import re
import sys
sys.path.append('../99_helpers/')
from test_helpers import print_log, print_check, print_crit_check  # noqa # pylint: disable=import-error
from test_helpers import print_test_summary, print_test_critical_failure  # noqa # pylint: disable=import-error
from test_helpers import get_process_returncode, get_process_output  # noqa # pylint: disable=import-error


# The actual IPs to compare to DNS results
main_ip = '192.168.10.1'
alt_ip = '192.168.10.101'

# The three hostnames to check
main_hostname = 'web.psa-team10.in.tum.de'
cname_hostname = 'www2.psa-team10.in.tum.de'
alt_ip_hostname = 'www3.psa-team10.in.tum.de'

# Keys for checking whether page was served correctly
main_key = 'Test'
cgi_key = "Hello world from user rech!"
cname_key = 'PUT SOMETHING HERE'
alt_ip_key = 'PUT SOMETHING HERE'

# Logging
access_log_path = '/var/log/nginx/'
access_log_name = 'access.log'
error_log_path = '/var/log/nginx/'
error_log_name = 'error.log'


def get_page(url):
    """ Uses curl to get the specified url
    """
    cmd = "curl --noproxy \"*\" -s {0}".format(url)
    return get_process_output(cmd)


def get_logs(path, name, filter_ips=False):
    """ Opens all the log files in specified path with specified name and
        returns their content as a list containing all lines.

        When filter_ips is true, a regex is used to extract lines containing
        IP addresses.
    """
    files = os.listdir(path)
    logs = [(path + file) for file in files if file.startswith(name)]
    lines = []
    for log in logs:
        with open(log, 'r') as log_file:
            lines += log_file.readlines()
    if filter_ips:
        # Set up regex pattern
        r = re.compile(r'((\d?\d?\d\.){3}\d?\d?\d)')
        # Use r.search on every line, then remove non-matches
        lines = list(filter(None, map(r.search, lines)))
        # Extract the group (=IP) from regex matches
        lines = list(map(lambda x: x.group(1), lines))
    return lines


# First, check whether nginx is even active
print_log("Checking nginx active")
cmd = "systemctl is-active --quiet nginx.service"
print_crit_check(get_process_returncode(cmd) == 0)

# Check whether DNS resolves to specified IPs
log_msg = "Checking DNS for {0}"
cmd = "host {0}"
print_log(log_msg.format("the main hostname"))
out = get_process_output(cmd.format(main_hostname))
print_crit_check(main_ip in out)
print_log(log_msg.format("the cname hostname"))
out = get_process_output(cmd.format(cname_hostname))
print_check(main_ip in out)
print_log(log_msg.format("the alt. hostname"))
out = get_process_output(cmd.format(alt_ip_hostname))
print_check(alt_ip in out)

# Check whether different hostnames return the correct keys
log_msg = "Checking hostname honored ({0})"
cmd = "curl --noproxy \"*\" -s {0}"
print_log(log_msg.format("main"))
print_check(main_key in get_page(main_hostname))
print_log(log_msg.format("cname"))
print_check(cname_key in get_page(cname_hostname))
print_log(log_msg.format("alt"))
print_check(alt_ip_key in get_page(alt_ip_hostname))


# Check whether CGI is run by user, not www-data
print_log("Checking CGI user")
# TODO: Implement CGI user test
print_check(False)


# Checking logfiles
print_log("Checking IPs in access log")
access_logs = get_logs(access_log_path, access_log_name, filter_ips=True)
print_check(len(access_logs) == 0)
print_log("Checking IPs in error log")
# Generating error to make sure error log isn't empty
get_process_returncode(cmd.format(main_hostname + '/idontexist.filetype'))
error_logs = get_logs(error_log_path, error_log_name, filter_ips=True)
print_check(len(error_logs) > 0)


# Check logrotate
print_log("Checking whether logrotate is active")
# TODO: Implement logrotate active test
print_check(False)
print_log("Checking whether old logs exist")
# TODO: Implment old logs exist test
print_check(False)


print_test_summary()
