#!/usr/bin/env python3.7

import threading
from sys import stdout
from time import sleep
from subprocess import run, Popen, PIPE

import sys
sys.path.append(sys.path[0] + '/../99_helpers/')
from test_helpers import get_process_output, get_process_returncode, get_vm_name  # noqa # pylint: disable=import-error
from test_helpers import print_log, print_check, print_crit_check, set_log_length  # noqa # pylint: disable=import-error
from test_helpers import print_test_summary  # noqa # pylint: disable=import-error

team_test_ip = '192.168.10.2'
team_router_ip = team_test_ip
praktikum_test_ip = '192.168.178.9.1'
proxy_ip = '131.159.0.2'


set_log_length(65)


def is_port_open(ip, port):
    cmd = f"nc -w5 -z {ip} {port}"
    return get_process_returncode(cmd) == 0


def is_local_port_open(port, run_server=True):
    def server():
        # Capture output to remove Address alread in use warnings
        process = Popen(f"exec nc -l {port}", shell=True, stderr=PIPE)
        sleep(30)
        process.kill()
        process.terminate()
    if run_server:
        t = threading.Thread(target=server)
        t.start()
    ip = '192.168.10.' + get_vm_name()[2:]
    cmd = f"ssh testing-vm nc -w5 -z {ip} {port}"
    cond = get_process_returncode(cmd) == 0
    return cond


# Check IP address
print_log("[NETWORK] IP address configured")
ip = get_process_output("ip -o -f inet addr show dev enp0s8")
print_crit_check("inet 192.168.10." in ip)
print_log("[NETWORK] Checking subnet mask")
print_check("/24 brd" in ip)

# Check team connection
print_log("[NETWORK] team subnet reachable")
cmd = "ping -c 5 -i 0.2 {0}".format(team_test_ip)
print_check(get_process_returncode(cmd) == 0)

# Check praktikum connection
print_log("[NETWORK] praktikum reachable")
cmd = "ping -c 5 -i 0.2 {0}".format(team_test_ip)
print_check(get_process_returncode(cmd) == 0)

# Check routes
print_log("[NETWORK] routes")
routes = get_process_output("ip route show | grep via | grep 192")
if get_vm_name() == "vm02":
    cond = ("192.168.1.0/24 via 192.168.101.1" in routes and
            "192.168.2.0/24 via 192.168.102.2" in routes and
            "192.168.3.0/24 via 192.168.103.3" in routes and
            "192.168.4.0/24 via 192.168.104.4" in routes and
            "192.168.5.0/24 via 192.168.105.5" in routes and
            "192.168.6.0/24 via 192.168.106.6" in routes and
            "192.168.7.0/24 via 192.168.107.7" in routes and
            "192.168.8.0/24 via 192.168.108.8" in routes and
            "192.168.9.0/24 via 192.168.109.9" in routes and
            "192.168.11.0/24 via 192.168.120.11" in routes)
else:
    cond = "192.168.0.0/16 via {0}".format(team_router_ip) in routes
print_check(cond)

# Check some firewall rules
cmd = "iptables -nL {0}"
tables = get_process_output(cmd)
out_tables = get_process_output(cmd.format('OUTPUT'))
in_tables = get_process_output(cmd.format('INPUT'))
raw_in_tables = get_process_output(cmd.format('PREROUTING -t raw'))
raw_out_tables = get_process_output(cmd.format('OUTPUT -t raw'))
print_log("[FIREWALL] policy drop")
cond = "policy DROP" in in_tables and "policy DROP" in out_tables
print_check(cond)
print_log("[FIREWALL] Port 123 closed")
print_check(not is_local_port_open(123))
print_log("[FIREWALL] Port 1234 closed")
print_check(not is_local_port_open(1234))

print_log("[FIREWALL] proxy connections possible")
print_check(is_port_open('131.159.0.2', 8080))

print_log("[FIREWALL] Incoming SSH possible")
print_check(is_local_port_open(22))
print_log("[FIREWALL] outgoing ssh possible (PSA network)")
print_check(is_port_open('192.168.8.1', 22))
print_log("[FIREWALL] outgoing ssh possible (faculty network)")
print_check(is_port_open('131.159.74.56', 22))
print_log("[FIREWALL] outgoing ssh not possible (outside faculty & PSA)")
print_check(not is_port_open('140.82.218.3', 22))

print_log("[FIREWALL] Port 80 open")
print_check(is_local_port_open(80))
print_log("[FIREWALL] Port 443 open")
print_check(is_local_port_open(443))

print_log("[FIREWALL] icmp allowed")
cond1 = "ACCEPT     icmp --  0.0.0.0/0            0.0.0.0/0" in out_tables
cond2 = "ACCEPT     icmp --  0.0.0.0/0            0.0.0.0/0" in in_tables
print_check(cond1 and cond2)
print_log("[FIREWALL] ICMP out possible")
print_check(get_process_returncode("ping 8.8.8.8 -c 5 -i 0") == 0)
print_log("[FIREWALL] ICMP in possible")
print_check(get_process_returncode("ssh testing-vm ping 8.8.8.8 -c 3") == 0)

print_log("[FIREWALL] NOTRACK active")
cond1 = ("tcp  --  0.0.0.0/0            0.0.0.0/0            tcp dpt:80 NOTRACK" in raw_in_tables and
         "tcp  --  0.0.0.0/0            0.0.0.0/0            tcp dpt:443 NOTRACK" in raw_in_tables)
cond2 = ("tcp  --  0.0.0.0/0            0.0.0.0/0            tcp spt:80 NOTRACK" in raw_out_tables and
         "tcp  --  0.0.0.0/0            0.0.0.0/0            tcp spt:443 NOTRACK" in raw_out_tables)
print_check(cond1 and cond2)


# Check IP address using http and https (is proxy connected?)
# Sourcing the bashrc and setting of proxy environment variables happens
# automatically in interactive terminals - tests might run non-interactively,
# though, so set them manually
with open('/etc/profile.d/proxy.sh', 'r') as f:
    proxies = f.read().replace('export ', '').splitlines()
cmd = "{0} curl -s {1}://ipecho.net/plain"
print_log("[PROXY] http proxy")
http_ip = get_process_output(cmd.format(proxies[0], 'http'))
print_check(http_ip == proxy_ip)
print_log("[PROXY] https proxy")
https_ip = get_process_output(cmd.format(proxies[1], 'https'))
print_check(https_ip == proxy_ip)

print_test_summary()
