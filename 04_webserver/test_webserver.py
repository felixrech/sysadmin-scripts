#!/usr/bin/env python3.7

import os
import re
import sys
sys.path.append(sys.path[0] + '/../99_helpers/')
from test_helpers import filter_list_by_regex  # noqa # pylint: disable=import-error
from test_helpers import print_log, print_check, print_crit_check  # noqa # pylint: disable=import-error
from test_helpers import get_process_returncode, get_process_output  # noqa # pylint: disable=import-error
from test_helpers import print_test_summary, print_test_critical_failure  # noqa # pylint: disable=import-error


# The actual IPs to compare to DNS results
main_ip = '192.168.10.1'
alt_ip = '192.168.10.201'

# The three hostnames to check
main_hostname = 'psa-team10.in.tum.de'
cname_hostname = 'www2.psa-team10.in.tum.de'
alt_ip_hostname = 'www3.psa-team10.in.tum.de'

# Keys for checking whether page was served correctly
main_key = 'PSA-T10-1'
cgi_key = "Hello world from user rech!"
cname_key = 'PSA-T10-2'
alt_ip_key = 'PSA-T10-3'

# Logging
access_log_path = '/var/log/nginx/'
access_log_name = 'access.log'
error_log_path = '/var/log/nginx/'
error_log_name = 'error.log'


def get_page(url):
    """ Uses curl to get the specified url
        Curl options used are:
         - Do not use proxy: --noproxy "*"
         - Print only content: -s
         - Accept all certificates: --insecure
         - https protocol
    """
    cmd = "curl --noproxy \"*\" -s --insecure https://{0}".format(url)
    return get_process_output(cmd)


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
print_log("Checking resolving to different IPs")
cond = (get_process_output(cmd.format(main_hostname))
        != get_process_output(cmd.format(alt_ip_hostname)))
print_check(cond)

# Check whether different hostnames return the correct keys
log_msg = "Checking hostname honored ({0})"
print_log(log_msg.format("main"))
main_page = get_page(main_hostname)
cname_page = get_page(cname_hostname)
alt_ip_page = get_page(alt_ip_hostname)
print_check(main_key in main_page)
print_log(log_msg.format("cname"))
print_check(cname_key in cname_page)
print_log(log_msg.format("alt"))
print_check(alt_ip_key in alt_ip_page)
print_log("Checking pages different")
print_check(len(set([main_page, cname_page, alt_ip_page])) == 3)


# Check whether CGI is run by user, not www-data
print_log("Checking CGI user")
# TODO: Implement CGI user test
print_check(False)


# Checking logfiles
print_log("Checking IPs in access log")
_, access_logs = get_logs(access_log_path, access_log_name, filter_ips=True)
print_check(len(access_logs) == 0)
print_log("Checking IPs in error log")
# Generating error to make sure error log isn't empty
get_process_returncode(cmd.format(main_hostname + '/idontexist.filetype'))
_, error_logs = get_logs(error_log_path, error_log_name, filter_ips=True)
print_check(len(error_logs) > 0)


# Check logrotate
access_files, access_logs = get_logs(access_log_path, access_log_name)
error_files, error_logs = get_logs(error_log_path, error_log_name)
print_log("Checking whether logrotate is active")
print_check(len(access_files) == 2 and len(error_files) == 6)


print_test_summary()
