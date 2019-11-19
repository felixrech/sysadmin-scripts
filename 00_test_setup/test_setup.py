import sys
import json
from subprocess import run
from itertools import compress

sys.path.append('../99_helpers/')
from test_helpers import print_log, print_check, get_process_output  # noqa # pylint: disable=import-error


python_version = 'python3.7'


with open('test_config.json', 'r') as config_file:
    config = json.load(config_file)

# Hostname is vmXX where XX are the digits at the end of the Linux hostname
# hostname = 'vm' + get_process_output('hostname')[-3:-1]
hostname = 'vm01'
dir = get_process_output('cd .. && pwd')[:-1] + '/'
test_seperator = ("\nprintf \"\\n\\nPress a key to continue to next test\""
                  "&& read -n 1 -s && clear\n")

for week in config:
    # Read which tests we need to install
    tests = list(config[week]['files'].keys())
    install_here = [hostname in config[week]['files'][test] for test in tests]
    to_install = list(compress(tests, install_here))
    # Prepare the root script's name and content
    test_script = '/root/PSA_test{0}.sh'.format(config[week]['week'])
    calls = ["{0} {1}{2}".format(python_version, dir, test)
             for test in to_install]
    test_script_content = test_seperator.join(calls)
    # Log what we're going to do in case of errors
    print_log(
        "Installing {0} of {1} file(s) for {2} into {3}".format(
            len(to_install),
            len(tests),
            week,
            test_script),
        fill=75)
    print("'''''\n" + test_script_content + "\n''''''")
    with open(test_script, 'w') as test_script_file:
        test_script_file.write(test_script_content)
    run("chmod +x {0}".format(test_script), shell=True)
    print_check(True)
