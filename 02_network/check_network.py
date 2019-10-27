from subprocess import check_output

failed_tests = 0


def print_check(b):
    if b:
        print("\t[OK]")
    else:
        print("\t\033[0;31m[FAIL]\033[0m")
        global failed_tests
        failed_tests += 1


# Check IP address using http and https (is proxy connected?)
tum_proxy_ip = '131.159.0.2'
cmd = "curl -s {0}://ipecho.net/plain"
print("Checking http proxy", end='')
http_ip = check_output(cmd.format('http'), shell=True).decode('utf-8')
print_check(http_ip == tum_proxy_ip)
print("Checking https proxy", end='')
https_ip = check_output(cmd.format('https'), shell=True).decode('utf-8')
print_check(https_ip == tum_proxy_ip)

# Print summary
if failed_tests == 0:
    print("\nAll tests passed!")
else:
    print("\n{0} tests failed!".format(failed_tests))
