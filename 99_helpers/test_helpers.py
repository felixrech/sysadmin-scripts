from sys import stdout, exit
from time import sleep
from subprocess import run, Popen, PIPE


failed_tests = 0


def print_log(msg):
    """ Print msg as description of current test """
    print(msg.ljust(40), end='...')
    stdout.flush()


def print_check(condition):
    """ Print condition as test passed/failed message and adjust failed_tests
        variable
    """
    if condition:
        print("\b\b\b\033[0;32m[OK]\033[0m")
    else:
        print("\b\b\b\033[0;31m[FAIL]\033[0m")
        global failed_tests
        failed_tests += 1
    stdout.flush()


def print_test_summary():
    """ Print a summary of the tests conducted """
    global failed_tests
    if failed_tests == 0:
        print("\nAll tests passed!")
    else:
        print("\n{0} test(s) failed!".format(failed_tests))


def print_test_critical_failure():
    """ Warns the user that a critical failure during tests occured
        and exits
    """
    print("\n\b\b\b\033[0;31m<<CRITICAL TEST FAILURE OCCURED>>\033[0m")
    print(("Stopping tests prematurely, "
           "since other tests might fail or be unreliable..."))
    exit()


def get_process_output(cmd):
    """ Runs cmd and returns the output """
    process = run(cmd, capture_output=True, shell=True)
    return process.stdout.decode('utf-8')


def get_process_returncode(cmd):
    """ Runs cmd and returns the return code """
    process = run(cmd, capture_output=True, shell=True)
    return process.returncode


def get_timeout_process_output(cmd, timeout):
    """ Runs cmd for timeout seconds, then kills and returns output """
    process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    sleep(timeout)
    process.kill()
    return process.stdout.read().decode('utf-8')
