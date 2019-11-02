#!/usr/bin/env python3.7

from sys import stdout
from subprocess import run, Popen, PIPE

own_ip = '192.168.10.1'
team_test_ip = '192.168.10.2'
team_router_ip = team_test_ip
praktikum_test_ip = '192.168.178.9.1'
proxy_ip = '131.159.0.2'

failed_tests = 0


def print_log(msg):
    print(msg.ljust(40), end='...')
    stdout.flush()


def print_check(b):
    if b:
        print("\b\b\b\033[0;32m[OK]\033[0m")
    else:
        print("\b\b\b\033[0;31m[FAIL]\033[0m")
        global failed_tests
        failed_tests += 1


def get_process_output(cmd):
    process = run(cmd, capture_output=True, shell=True)
    return process.stdout.decode('utf-8')


def get_process_returncode(cmd):
    process = run(cmd, capture_output=True, shell=True)
    return process.returncode


def run_parallel_output(output_cmd, other_cmd, other_input):
    output_p = Popen(output_cmd, stdout=PIPE, stderr=PIPE, shell=True)
    other_p = Popen(
        other_cmd,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        shell=True)
    other_p.communicate(bytes(other_input, 'utf-8'))
    other_p.terminate()
    other_p.wait()
    output_p.wait()
    return output_p.stdout.read().decode('utf-8')


# Check IP address
print_log("[NETWORK] IP address configured")
cmd = "ip addr show enp0s8"
configuration = get_process_output(cmd)
print_check("inet {0}/24".format(own_ip) in configuration)

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
cmd = "ip route show"
routes = get_process_output(cmd)
cond_check = "192.168.0.0/16 via {0}".format(team_router_ip) in routes
print_check(cond_check)

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
print_log("[FIREWALL] incoming ssh allowed")
cond1 = "ACCEPT     tcp  --  0.0.0.0/0            0.0.0.0/0            tcp spt:22 ctstate RELATED,ESTABLISHED" in out_tables
cond2 = "ACCEPT     tcp  --  0.0.0.0/0            0.0.0.0/0            tcp dpt:22" in in_tables
print_check(cond1 and cond2)
print_log("[FIREWALL] outgoing ssh allowed")
print_check(get_process_returncode("ssh -o StrictHostKeyChecking=no github.com") == 255)
print_log("[FIREWALL] icmp allowed")
cond1 = "ACCEPT     icmp --  0.0.0.0/0            0.0.0.0/0" in out_tables
cond2 = "ACCEPT     icmp --  0.0.0.0/0            0.0.0.0/0" in in_tables
print_check(cond1 and cond2)
print_log("[FIREWALL] proxy connections allowed")
cond1 = "ACCEPT     tcp  --  131.159.0.2          0.0.0.0/0            tcp dpt:8080" in out_tables
cond2 = "ACCEPT     tcp  --  0.0.0.0/0            131.159.0.2          tcp spt:8080 ctstate RELATED,ESTABLISHED" in in_tables
print_check(cond1 and cond2)
print_log("[FIREWALL] NOTRACK active")
cond1 = ("tcp  --  0.0.0.0/0            0.0.0.0/0            tcp dpt:80 NOTRACK" in raw_in_tables and
         "tcp  --  0.0.0.0/0            0.0.0.0/0            tcp dpt:443 NOTRACK" in raw_in_tables)
cond2 = ("tcp  --  0.0.0.0/0            0.0.0.0/0            tcp spt:80 NOTRACK" in raw_out_tables and
         "tcp  --  0.0.0.0/0            0.0.0.0/0            tcp spt:443 NOTRACK" in raw_out_tables)
print_check(cond1 and cond2)

# Check IP address using http and https (is proxy connected?)
cmd = "curl -s {0}://ipecho.net/plain"
print_log("[PROXY] http proxy")
http_ip = get_process_output(cmd.format('http'))
print_check(http_ip == proxy_ip)
print_log("[PROXY] https proxy")
https_ip = get_process_output(cmd.format('https'))
print_check(https_ip == proxy_ip)

# Print summary
if failed_tests == 0:
    print("\nAll tests passed!")
else:
    print("\n{0} test(s) failed!".format(failed_tests))
