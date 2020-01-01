import os
from subprocess import run


admin_pw = input("Please enter admin password: ")


def get_template(key):
    with open('srcs/{}.template'.format(key), 'r') as f:
        return f.read()


def create_ldif(template, format_dict, filename):
    # Create folder if necessary
    mkdir_p(filename.split('/')[0])
    # Load ldif template, format and write it to file
    ldif = get_template(template)
    with open(filename, 'w') as f:
        f.write(ldif.format_map(format_dict))


def add_ldif(filename):
    cmd = "ldapadd -w {0} -H ldapi:/// -D \"cn=admin,dc=team10,dc=psa,dc=in,dc=tum,dc=de\" -f {1}"
    run(cmd.format(admin_pw, filename), shell=True)


def mkdir_p(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
