import json
import subprocess


def run_cmd(cmd):
    print(cmd)
    subprocess.call(cmd, shell=True)


# Load names, uids and keys from json
uid_file = open('uids.json', 'r')
uids = json.load(uid_file)

# For each user
for user in uids:
    # Delete user
    cmd = "userdel {0}".format(user['name'])
    run_cmd(cmd)
    # Delete user's home directory
    cmd = "rm -rf /home/{0}".format(user['name'])
    run_cmd(cmd)

# Delete psa-user group
cmd = "groupdel psa-user"
run_cmd(cmd)

