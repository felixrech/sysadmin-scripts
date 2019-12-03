#!/usr/bin/env python3.7

import os
import re
import sys
sys.path.append(sys.path[0] + '/../99_helpers/')
from test_helpers import get_page, filter_list_by_regex  # noqa # pylint: disable=import-error
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

print_test_summary()
