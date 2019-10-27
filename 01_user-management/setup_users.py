import json
import subprocess


def run_cmd(cmd):
    print(cmd)
    subprocess.call(cmd, shell=True)


# Add psa-user group
cmd = "groupadd psa-user --gid 10025"
run_cmd(cmd)

# Load names, uids and keys from json
uid_file = open('uids.json', 'r')
uids = json.load(uid_file)

# For each user
for user in uids:
    # Add user, create home directory and add to psa-user group
    cmd = "useradd --uid {0} -g 10025 --create-home --shell /bin/bash {1}".format(
        user['id'], user['name'])
    run_cmd(cmd)
    # By default, SSH will not let allow accounts with locked passwords
    # (default when account is created without a password) login, so
    # set an impossible password
    # Source: https://arlimus.github.io/articles/usepam/
    cmd = "usermod -p \"*\" {0}".format(user['name'])
    run_cmd(cmd)
    # Create .ssh/ directory, add key to authorized_keys and own .ssh/
    cmd = "mkdir /home/{0}/.ssh/".format(user['name'])
    run_cmd(cmd)
    cmd = "echo \"{0}\" >> /home/{1}/.ssh/authorized_keys".format(
        user['sshKey'], user['name'])
    run_cmd(cmd)
    cmd = "chown {0}:10025 -R /home/{1}/.ssh/".format(user['id'], user['name'])
    run_cmd(cmd)
    # Limit home directory access to owners
    cmd = "chmod -R 700 /home/{0}".format(user['name'])
    run_cmd(cmd)
    # If root, add to sudo group
    if user['root']:
        cmd = "usermod -a -G sudo {0}".format(user['name'])
        run_cmd(cmd)
    print()
