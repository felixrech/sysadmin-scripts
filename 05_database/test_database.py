#!/usr/bin/env python3.7

import sys
import secrets
import pymysql
sys.path.append(sys.path[0] + '/../99_helpers/')
from test_helpers import filter_list_by_regex  # noqa # pylint: disable=import-error
from test_helpers import print_log, print_check, print_crit_check  # noqa # pylint: disable=import-error
from test_helpers import get_process_returncode, get_process_output  # noqa # pylint: disable=import-error
from test_helpers import print_test_summary, print_test_critical_failure  # noqa # pylint: disable=import-error


log_fill = 70
readonly_user = 'readonly'
# TODO: save password into a config file
readonly_pwd = input("Please enter readonly user's password: ")
localhost_user = 'test_user1'
# TODO: save password into a config file
localhost_pwd = input("Please enter localhost user's password: ")
localhost_db = 'test_db1'
localhost_test_table = 'test_table'
remote_user = 'test_user2'
remote_host = '192.168.10.4'
remote_db = 'test_db2'
replication_user = 'replication'
replication_host = '192.168.10.4'

localhost_string = localhost_user + '@localhost'
remote_string = '{0}@{1}'.format(remote_user, remote_host)
readonly_string = readonly_user + '@localhost'
replication_string = '{0}@{1}'.format(replication_user, replication_host)
expected_users = set([localhost_string,
                      remote_string,
                      readonly_string,
                      replication_string,
                      'root@localhost',
                      'mysql@localhost'])


def sql_query(c, sql, args=()):
    c.execute(sql, args)
    return [tup[0] for tup in c.fetchall()]


def get_grants_of(c, user, host):
    grants = sql_query(c, "show grants for %s@%s;", (user, host))
    cleaned_grants = [g for g in grants if not g.startswith("GRANT USAGE")]
    return cleaned_grants


def generate_token(c):
    test_token = secrets.token_urlsafe(48)[0:48]
    with c.cursor() as cur:
        sql = ("select * from {0}.{1} where test_secret = %s;"
               .format(localhost_db, localhost_test_table))
        read_tokens = sql_query(cur, sql, (test_token, ))
    if not test_token in read_tokens:
        return test_token
    else:
        return generate_token(c)


# First, check whether mariadb is even active
print_log("Checking database server active", fill=log_fill)
cmd = "systemctl is-active --quiet mariadb.service"
print_crit_check(get_process_returncode(cmd) == 0)

# Try logging in with readonly user
print_log("Checking readonly user can log in", fill=log_fill)
readonly_con = pymysql.connect(
    host='localhost',
    user=readonly_user,
    password=readonly_pwd)
print_crit_check(True)

# We just logged in using the readonly user, so it exists
print_log("Checking readonly user exists", fill=log_fill)
print_check(True)

with readonly_con.cursor() as read_cursor:
    # Test whether the required users exist
    sql = "select concat(user, '@', host) from mysql.user;"
    users = sql_query(read_cursor, sql)
    print_log("Checking localhost user exists", fill=log_fill)
    print_check(localhost_string in users)
    print_log("Checking remote user exists", fill=log_fill)
    print_check(remote_string in users)
    print_log("Checking replication user exists", fill=log_fill)
    print_check(replication_string in users)

    # Test whether there are more than the expected users
    print_log("Checking whether unexpected users exist", fill=log_fill)
    unexpected_users = list(set(users) - set(expected_users))
    if len(unexpected_users) == 0:
        print_check(True)
    else:
        print('\n{0}'.format(unexpected_users))
        user_input = input("Are these valid users? Y/n")
        print_log("Checking whether unexpected users exist", fill=log_fill)
        print_check(user_input in ['', 'y', 'yes', 'Y'])

    print_log(
        "Checking required permissions for localhost user",
        fill=log_fill)
    test_string = "GRANT ALL PRIVILEGES ON `{0}`.*".format(localhost_db)
    grants = get_grants_of(read_cursor, localhost_user, 'localhost')
    print_check(any(grant for grant in grants if test_string in grant))
    print_log(
        "Checking additional permissions for localhost user",
        fill=log_fill)
    print_check(len(grants) == 1)

    print_log("Checking required permissions for remote user", fill=log_fill)
    test_string = "GRANT ALL PRIVILEGES ON `{0}`.*".format(remote_db)
    grants = get_grants_of(read_cursor, remote_user, remote_host)
    print_check(any(grant for grant in grants if test_string in grant))
    print_log("Checking additional permissions for remote user", fill=log_fill)
    print_check(len(grants) == 1)

    print_log("Checking required permissions for readonly user", fill=log_fill)
    test_string = "GRANT SELECT, SHOW DATABASES, SHOW VIEW ON *.*"
    grants = get_grants_of(read_cursor, readonly_user, 'localhost')
    print_check(any(grant for grant in grants if test_string in grant))
    print_log(
        "Checking additional permissions for readonly user",
        fill=log_fill)
    print_check(len(grants) == 1)

    print_log(
        "Checking required permissions for replication user",
        fill=log_fill)
    test_string = "GRANT REPLICATION SLAVE ON *.*"
    grants = get_grants_of(read_cursor, replication_user, replication_host)
    print_check(any(grant for grant in grants if test_string in grant))
    print_log(
        "Checking additional permissions for replication user",
        fill=log_fill)
    print_check(len(grants) == 1)


print_log("Checking database write and consequent read", fill=log_fill)
test_token = generate_token(readonly_con)
write_con = pymysql.connect(
    host='localhost',
    user=localhost_user,
    password=localhost_pwd,
    database=localhost_db)
with write_con.cursor() as write_cursor:
    sql = "insert into {0} values(%s);".format(localhost_test_table)
    write_cursor.execute(sql, (test_token,))
write_con.commit()
read_con = pymysql.connect(
    host='localhost',
    user=readonly_user,
    password=readonly_pwd,
    database=localhost_db)
with read_con.cursor() as read_cursor:
    sql = ("select * from {0} where test_secret = %s;"
           .format(localhost_test_table))
    tokens = sql_query(read_cursor, sql, (test_token,))
    print_check(test_token in tokens)

print_test_summary()
