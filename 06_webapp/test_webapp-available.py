import sys

sys.path.append(sys.path[0] + '/../99_helpers/')
from test_helpers import get_page  # noqa # pylint: disable=import-error
from test_helpers import print_log, print_check  # noqa # pylint: disable=import-error
from test_helpers import print_test_summary  # noqa # pylint: disable=import-error

print_log("Checking available in PSA network")
page = get_page('status.psa-team10.in.tum.de')
print_check("<title>Status app</title>" in page)

print_log("Checking available externally")
print_check("<title>Status app</title>" in get_page('psa.in.tum.de:61015'))

print_test_summary()
