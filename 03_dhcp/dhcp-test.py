import re
from sys import stdout
from time import sleep
from subprocess import Popen, PIPE

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
    stdout.flush()


def get_timeout_process_output(cmd, timeout):
    process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    sleep(timeout)
    process.kill()
    return process.stdout.read().decode('utf-8')


print("Warning: The first test will take 60 seconds to get dump of dhcp connections\n")
print_log("Checking dhcp server online")

# Get dhcp connection dump (exec needed for process to be killable)
cmd = "exec dhcpdump -i enp0s8 -h ^08:00:27:ee:9c:c1"
output = get_timeout_process_output(cmd, timeout=60)

# Check whether DHCPACK from VM01 exists and get it
seperator = '---------------------------------------------------------------------------'
packets = output.split(seperator)
regex = ".*\(8:0:27:b4:ff:be\) > (\d|\.)+ \(8:0:27:ee:9c:c1\)"
exists_dhcp_ack = any(p for p in packets if re.search(regex, p) is not None and "2 (BOOTPREPLY)" in p)
print_check(exists_dhcp_ack)
if not exists_dhcp_ack:
    print("Stopping tests prematurely, since other tests will fail")
reply = next(p for p in packets if re.search(regex, p) is not None and "2 (BOOTPREPLY)" in p)

# Check whether dhcp server delivers all the required information
print_log("Checking IP address assigned")
cond = "YIADDR: 192.168.10.1" in reply
print_check(cond)
print_log("Checking subnet mask specified")
cond = "OPTION:   1 (  4) Subnet mask               255.255.255.0" in reply
print_check(cond)
print_log("Checking host name specified")
cond = "OPTION:  12 ( 14) Host name                 vmpsateam10-01" in reply
print_check(cond)
print_log("Checking domain name specified")
cond = "OPTION:  15 ( 20) Domainname                psa-team10.in.tum.de" in reply
print_check(cond)
print_log("Checking dns server specified")
cond = "OPTION:   6 (  4) DNS server                192.168.10.2" in reply
print_check(cond)
print_log("Checking routes specified")
cond = "OPTION: 121 (  7) Classless Static Route    10c0a8c0a80a02" in reply
print_check(cond)

# Print summary
if failed_tests == 0:
    print("\nAll tests passed!")
else:
    print("\n{0} test(s) failed!".format(failed_tests))

