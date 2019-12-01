import sys
import json
from subprocess import run
from itertools import compress

sys.path.append(sys.path[0] + '/../99_helpers/')
from test_helpers import print_log, print_check, get_process_output  # noqa # pylint: disable=import-error


# Constants
python_version = 'python3.7'

# Hostname is vmXX where XX are the digits at the end of the Linux hostname
hostname = 'vm' + get_process_output('hostname')[-3:-1]
# Get full path to sysadmin-scripts folder
dir = get_process_output('cd .. && pwd')[:-1] + '/'
# Between tests we want to ask the user whether they want to continue and
# clean the screen
test_seperator = ("\nprintf \"\\n\\nPress a key to continue to next test\""
                  "&& read -n 1 -s && clear\n")

# Read in the configuration file for which tests and helpers to install
with open('tests_config.json', 'r') as config_file:
    config = json.load(config_file)


def get_files_to_install(week, category):
    """ Gets the files of given week and category.
        Then filters to those to be installed locally
    """
    files = list(config[week][category].keys())
    install_here = [hostname in config[week][category][f] for f in files]
    files_to_install = [dir + f for f in list(compress(files, install_here))]
    return files, files_to_install


def write_script(name, files, seperator):
    """ Writes a script that will execute the tests
    """
    # Set script's name and content
    script_name = '/root/{0}'.format(name)
    calls = ["{0} {1}".format(python_version, file) for file in files]
    script_content = seperator.join(calls)
    # Write the file and mark it executable
    with open(script_name, 'w') as script_file:
        script_file.write(script_content)
    run("chmod +x {0}".format(script_name), shell=True)


def install_for_automated_testing(tests):
    if len(tests) == 0:
        return
    print_log(("Installing {0} file(s) for automated testing"
               .format(len(tests))), fill=75)
    base = "/root/tests/"
    for test in tests:
        cmd = "ln -sf {0} {1}".format(test, base + test.split('_')[-1])
        run(cmd, shell=True)
    print_check(True)


# TODO Set permissions of folder so only current user and root can access
run("mkdir -p /root/tests", shell=True)
run("mkdir -p /root/helpers/", shell=True)

for week in config:
    # Read which tests we need to install
    tests, tests_to_install = get_files_to_install(week, 'tests')
    script_name = config[week]['script_name']

    # Log what we're going to do in case of errors
    log_msg = ("Installing {0} of {1} file(s) for {2} into {3}"
               .format(len(tests_to_install), len(tests), week, script_name))
    print_log(log_msg, fill=75)

    # Install script
    if len(tests_to_install) >= 1:
        write_script(script_name, tests_to_install, test_seperator)
    print_check(True)

    # Install tests for automatic testing
    install_for_automated_testing(tests_to_install)

    # Some tests need helper, let's check whether this week needs one as well
    if not 'helpers' in config[week].keys():
        continue
    _, helpers_to_install = get_files_to_install(week, 'helpers')
    if len(helpers_to_install) == 0:
        continue

    # Install the helpers in the /root/helpers/ folder
    log_msg = ("Installing {0} helper(s) for {1}"
               .format(len(helpers_to_install), week))
    print_log(log_msg, fill=75)
    for helper in helpers_to_install:
        cmd = "ln -s {0} /root/helpers/{1}"
        run(cmd.format(helper, helper.split('/')[-1]), shell=True)
    print_check(True)

    # Install the helpers as tests for automatic testing
    install_for_automated_testing(helpers_to_install)