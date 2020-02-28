import re
import sys
import json
from time import sleep
from sys import stdout, exit
from subprocess import run, Popen, PIPE


passed_tests = 0
failed_tests = 0
global_fill = 0


def set_log_length(length):
    """
    Sets the default log fill to given length.
    """
    global global_fill
    global_fill = length


def print_log(msg, fill=40):
    """ Print msg as description of current test """
    global global_fill
    if fill == 40 and global_fill > fill:
        fill = global_fill
    print(msg.ljust(fill), end='...')
    stdout.flush()


def print_check(condition):
    """ Print condition as test passed/failed message and adjust failed_tests
        variable
    """
    if condition:
        print("\b\b\b\033[0;32m[OK]\033[0m")
        global passed_tests
        passed_tests += 1
    else:
        print("\b\b\b\033[0;31m[FAIL]\033[0m")
        global failed_tests
        failed_tests += 1
    stdout.flush()


def print_crit_check(condition):
    """ Calls print_check and if condition failed
        print_test_critical_failure
    """
    print_check(condition)
    if not condition:
        print_test_critical_failure()


def print_test_summary():
    """ Print a summary of the tests conducted """
    global failed_tests
    summary = " ({0}/{1})".format(passed_tests, passed_tests+failed_tests)
    if failed_tests == 0:
        print("\nAll tests passed!{}".format(summary))
    else:
        print("\n{0} test(s) failed!{1}".format(failed_tests, summary))


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


def run_remote_test(vm, test_name, helper=True, arg=None):
    """
    Executes a different test script remotely on another VM.
    Prints either the output of the remote test or ssh-error message.

    :param vm: name of the vm (string, e.g. 'vm01')
    :param test_name: name of the test (string, e.g. 'ldap')
    :param helper: whether helper (True) or test (False), defaults to helper
    :param arg: argument(s) to script, string
    """
    # Add space before arg if given, otherwise replace prep to format by nothing
    arg = ' ' + arg if arg is not None else ''
    # Define the command for remote script execution
    cmd = "ssh {0} \"python3.7 /root/helpers/{1}.py{2}\" 2>&1"
    cmd = cmd.format(vm, test_name, arg)
    # If remote script is a test, change base path
    cmd = cmd if helper else cmd.replace('helpers', 'tests')
    # Execute remote script on given vm and save output
    process = run(cmd.format(vm, test_name), capture_output=True, shell=True)
    # Exit code 255 means an error in ssh, not the remote test
    if process.returncode == 255:
        print_log("Remote test execution failed because of ssh error...")
        print_check(False)
    # If test exited successfully, print tests, add passed/failed to statistics
    elif process.returncode == 0:
        out = process.stdout.decode('utf-8').splitlines()
        nums = out[-1][out[-1].find('(')+1:out[-1].find(')')].split('/')
        global passed_tests, failed_tests
        passed_tests += int(nums[0])
        failed_tests += int(nums[1]) - int(nums[0])
        print('\n'.join(out[:-2]))
    # Remote test failed, print error message
    else:
        print_log("Remote test execution failed")
        print_check(False)


def get_vm_name():
    """
    Returns the vm's name, e.g. 'vm01' or 'vm05'

    :returns: vm's name (string)
    """
    return 'vm' + get_process_output('hostname')[-3:-1]


def filter_list_by_regex(l, pattern, group=None):
    """ Compiles pattern and filters list down to matches.
        If group is specified, only returns the specified group (arg = #)
    """
    r = re.compile(pattern)
    filtered = list(filter(None, map(r.search, l)))
    if group is not None:
        filtered = list(map(lambda x: x.group(group), filtered))
    return filtered


def get_page(url, auth=None):
    """ Uses curl to get the specified url
        Curl options used are:
         - Do not use proxy: --noproxy "*"
         - Print only content: -s
         - Accept all certificates: --insecure
         - https protocol
         - Authentication if specified: -u
    """
    auth = '' if auth is None else ' -u ' + ':'.join(auth)
    cmd = "curl --noproxy \"*\" -s --insecure{0} https://{1}".format(auth, url)
    return get_process_output(cmd)


def exists_mount(src, to):
    """
    Checks whether a mount of given source exists to given destination using
    parsed df -h output.

    :param src: source (string, e.g. '192.168.10.6:/myfolder')
    :param to: destination (string, e.g. '/mnt/myfolder')
    :returns: boolean
    """
    mounts = get_process_output("df -h").splitlines()
    return any([l.startswith(src) and l.endswith(to) for l in mounts])


def read_config(item):
    # TODO: document
    with open('/root/.config.json', 'r') as f:
        config = json.load(f)
    return config[item]


class Cursor(object):
    """
    Returns a database read-only cursor for use in with statements.

    This is a read-only cursor, changes are not committed.

    Usage:
        with Cursor() as c:
            c.execute(read_sql)
    """

    def __init__(self, host=None, port=3306, user=None, pw=None, db=None):
        import pymysql
        self.db = pymysql.connect(
            host=host if host is not None else read_config('SQL-host'),
            user=user if user is not None else read_config('SQL-user'),
            password=pw if pw is not None else read_config('SQL-pw'),
            database=db if db is not None else read_config('SQL-database'))

    def __enter__(self):
        return self.db.cursor()

    def __exit__(self, exc_type, exc_val, trace):
        self.db.close()


class WriteCursor(Cursor):
    """
    Returns a database cursor for use in with statements.

    Will commit changes made using the cursor.

    Usage:
        with WriteCursor() as c:
            c.execute(write_sql)
    """

    def __exit__(self, exc_type, exc_val, trace):
        self.db.commit()
        super().__exit__(exc_type, exc_val, trace)


def is_interactive():
    return len(sys.argv) > 1 and sys.argv[1] == '-i'
