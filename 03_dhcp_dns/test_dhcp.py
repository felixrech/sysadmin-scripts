#!/usr/bin/env python3.7

import sys
sys.path.append(sys.path[0] + '/../99_helpers/')
from test_helpers import print_log, print_check, print_crit_check  # noqa # pylint: disable=import-error
from test_helpers import print_test_summary  # noqa # pylint: disable=import-error
from test_helpers import get_process_output  # noqa # pylint: disable=import-error


print_log("Checking netplan dhcp")
with open('/etc/netplan/psa.yaml', 'r') as f:
    netplan = f.read()
print_crit_check('dhcp4: true' in netplan)

print_log("Checking IP address assigned")
ip = get_process_output("ip -o -f inet addr show dev enp0s8 dynamic")
print_crit_check("inet 192.168.10." in ip)

print_log("Checking subnet mask specified")
print_check("/24 brd" in ip)

print_log("Checking routes specified")
routes = get_process_output("ip route list proto dhcp dev enp0s8")
print_check("192.168.0.0/16 via 192.168.10.2" in routes)

print_test_summary()
