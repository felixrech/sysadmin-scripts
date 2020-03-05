import sys

sys.path.append(sys.path[0] + '/../99_helpers/')
from test_helpers import get_process_output  # noqa # pylint: disable=import-error
from test_helpers import set_log_length, print_log, print_check, print_crit_check  # noqa # pylint: disable=import-error
from test_helpers import print_test_summary  # noqa # pylint: disable=import-error


set_log_length(65)


# Get the test_token
if len(sys.argv) < 1:
    print_log("[SPAM/VIRUS] secret not specified")
    print_crit_check(False)
ts = sys.argv[1]


print_log("[SPAM/VIRUS] Spam e-mail dropped message in mail.log")
out = get_process_output(
    f"cat /var/log/mail.log | grep \"spam-{ts}@psa.in.tum.de\"")
print_check(out != '')

print_log("[SPAM/VIRUS] Virus e-mail dropped message in mail.log")
out = get_process_output(
    f"cat /var/log/mail.log | grep \"virus-{ts}@psa.in.tum.de\"")
print_check(out != '')

print_test_summary()
