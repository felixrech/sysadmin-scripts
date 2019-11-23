#!/usr/bin/env python3.7

import re
import sys
sys.path.append(sys.path[0] + '/../99_helpers/')
from test_helpers import print_log, print_check, print_crit_check  # noqa # pylint: disable=import-error
from test_helpers import print_test_summary  # noqa # pylint: disable=import-error
from test_helpers import get_process_output, get_process_returncode  # noqa # pylint: disable=import-error


# Declare constants
server_dns, server_ip = 'dns.psa-team10.in.tum.de.', '192.168.10.2'
vm1_dns, vm1_ip = 'vm1.psa-team10.in.tum.de.', '192.168.10.1'
team_dns, team_ip = 'psa-team10.in.tum.de.', '192.168.10.1'
team_one_dns, team_one_ip = 'dns.psa-team01.in.tum.de.', '192.168.1.3'
tum_proxy_dns, tum_proxy_ip = 'proxy.in.tum.de.', '131.159.0.2'


# First, check whether bind9 is even active if same VM
if "inet " + server_ip + '/' in get_process_output("ip addr show"):
    print_log("Checking bind9 active")
    cmd = "systemctl is-active --quiet bind9.service"
    print_crit_check(get_process_returncode(cmd) == 0)


cmd = "host {0} " + server_ip

# Do tests for team domain names
print_log("Checking dns A record")
print_check(server_ip in get_process_output(cmd.format(server_dns)))
print_log("Checking team A record")
print_check(team_ip in get_process_output(cmd.format(team_dns)))
print_log("Checking vm1 A record")
print_check(vm1_ip in get_process_output(cmd.format(vm1_dns)))

# Do tests for other team's domain names
print_log("Checking other team's records")
print_check(team_one_ip in get_process_output(cmd.format(team_one_dns)))

# Do tests for non-PSA domain names
print_log("Checking real-world A records")
print_check(tum_proxy_ip in get_process_output(cmd.format(tum_proxy_dns)))

# Test reverse lookup
print_log("Checking reverse lookup")
records = get_process_output(cmd.format(team_ip))
print_check("domain name pointer " + team_dns in records)
