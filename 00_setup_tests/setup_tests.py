import sys
import json
from subprocess import run
from itertools import compress

sys.path.append(sys.path[0] + '/../99_helpers/')
from test_helpers import get_vm_name  # noqa # pylint: disable=import-error
from test_helpers import print_log, print_check, get_process_output, set_log_length  # noqa # pylint: disable=import-error


# Constants
python_version = 'python3.7'

# Hostname is vmXX where XX are the digits at the end of the Linux hostname
hostname = get_vm_name()
# Get full path to sysadmin-scripts folder
dir = get_process_output('cd .. && pwd')[:-1] + '/'
# Between tests we want to ask the user whether they want to continue and
# clean the screen
test_seperator = ("\nprintf \"\\n\\nPress a key to continue to next test\""
                  "&& read -n 1 -s && printf \"\\n\\n\"\n")

# Read in the configuration file for which tests and helpers to install
with open('tests_config.json', 'r') as config_file:
    config = json.load(config_file)

# Set log length to 50
set_log_length(50)


def get_files_to_install(week, category):
    """
    Gets the files of given week and category filtered down to those to be
    installed locally.

    :param week: files of which week to look at (string, e.g. 'dns')
    :param category: tests or helpers (string)
    :returns: list of source files (list of strings)
    """
    files = list(config[week][category].keys())
    install_here = [hostname in config[week][category][f] for f in files]
    files_to_install = [dir + f for f in list(compress(files, install_here))]
    return files_to_install


def extract_name(test_name):
    return test_name.split('_')[-1]


def write_script(name, files, seperator):
    """ Writes a script that will execute the tests
    """
    # Set script's name and content
    script_name = '/root/{0}'.format(name)
    files = list(map(extract_name, files))
    calls = ["{0} /root/tests/{1}".format(python_version, file)
             for file in files]
    script_content = seperator.join(calls)
    # Write the file and mark it executable
    with open(script_name, 'w') as script_file:
        script_file.write(script_content)
    run("chmod +x {0}".format(script_name), shell=True)


def install_files(files, destination):
    for file_name in files:
        # '/.../test_ldap.py' -> '<destination>/ldap.py
        install_name = destination + '/' + extract_name(file_name)
        # Copy file to destination
        run("cp {0} {1}".format(file_name, install_name), shell=True)


def install_tests(tests, week):
    print_log("Installing {0} test file(s) for {1}".format(len(tests), week))
    install_files(tests, '/root/tests')
    print_check(True)


def install_helpers(helpers, week):
    msg = "Installing {0} helper file(s) for {1}".format(len(helpers), week)
    print_log(msg)
    install_files(helpers, '/root/helpers')
    print_check(True)


if __name__ == "__main__":
    # Setup folders
    run("mkdir -p /root/tests", shell=True)
    run("mkdir -p /root/helpers/", shell=True)

    # Copy test_helpers
    cmd = "cp ../99_helpers/test_helpers.py /root/{}/test_helpers.py"
    run(cmd.format('tests'), shell=True)
    run(cmd.format('helpers'), shell=True)

    for week in config:
        # Read which tests we need to install
        tests_to_install = get_files_to_install(week, 'tests')
        script_name = config[week]['script_name']

        # Install tests and helpers
        if len(tests_to_install) > 0:
            install_tests(tests_to_install, week)

        # Install script
        if len(tests_to_install) >= 1:
            write_script(script_name, tests_to_install, test_seperator)

        # Some tests need helpers
        if not 'helpers' in config[week].keys():
            continue
        helpers_to_install = get_files_to_install(week, 'helpers')
        if len(helpers_to_install) > 0:
            install_helpers(helpers_to_install, week)
