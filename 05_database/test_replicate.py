#!/usr/bin/env python3.7

import sys
import pymysql
from os import listdir
from datetime import datetime, timedelta
sys.path.append(sys.path[0] + '/../99_helpers/')
from test_helpers import get_process_returncode, read_config  # noqa # pylint: disable=import-error
from test_helpers import set_log_length, print_log, print_check, print_crit_check  # noqa # pylint: disable=import-error
from test_helpers import print_test_summary  # noqa # pylint: disable=import-error


set_log_length(70)
readonly_user = 'readonly'
readonly_pwd = read_config('database-readonly-pw')
test_db = 'test_db1'
test_table = 'test_table'


def sql_query(c, sql, args=()):
    c.execute(sql, args)
    return [tup[0] for tup in c.fetchall()]


# Get the test_token
if len(sys.argv) == 1 and len(sys.argv[1]) != 48:
    print_log("Test token specified")
    print_crit_check(False)
test_token = sys.argv[1]


# First, check whether mariadb is even active
print_log("Checking replication server active")
cmd = "systemctl is-active --quiet mariadb.service"
print_check(get_process_returncode(cmd) == 0)

# Try logging in with readonly user
print_log("Checking readonly user can log in to replication")
readonly_con = pymysql.connect(
    host='localhost',
    user=readonly_user,
    password=readonly_pwd,
    database=test_db)
print_check(True)

# Test whether the token written on master is also on replication
print_log("Checking data replication")
with readonly_con.cursor() as read_cursor:
    sql = ("select * from {0} where test_secret = %s;"
           .format(test_table))
    tokens = sql_query(read_cursor, sql, (test_token,))
    print_check(test_token in tokens)

# Test whether we have a backup of yesterday's database state
print_log("Checking database backups")
yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d.gz')
print_check(yesterday in listdir('/var/mariadb/backups'))

print_test_summary()
