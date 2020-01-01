from subprocess import run
from common import get_template, mkdir_p, create_ldif, add_ldif


def setup():
    print("Creating student schema ldif, slaptest output follows:\n")
    # Read in slaptest configuration file template
    conf = get_template('conf')
    # Format placeholder with the schema file path
    conf = conf.format_map({'pwd': os.getcwd()})
    # Create a temporary directory for slaptest output
    mkdir_p('tmpdir')
    # Write slaptest configuration file
    with open('tmpdir/student.conf', 'w') as f:
        f.write(conf)
    # Let slaptest create a ldif
    run("slaptest -f tmpdir/student.conf -F tmpdir/", shell=True)

    print("\nInstalling schema")
    # Read schema ldif and remove unnecessary lines
    with open('tmpdir/cn=config/cn=schema/cn={1}student.ldif', 'r') as f:
        ldif = f.read().splitlines()[5:-7]
    # Add some required lines
    ldif = ["dn: cn=student,cn=schema,cn=config",
            "objectClass: olcSchemaConfig",
            "cn: student"] + ldif
    # Write ldif file
    with open('tmpdir/add_student_schema.ldif', 'w') as f:
        f.write('\n'.join(ldif) + '\n')
    # Add schema to configuration
    run("ldapadd -Y EXTERNAL -H ldapi:/// -D \"cn=config\" -f tmpdir/add_student_schema.ldif", shell=True)
    # add_ldif("tmpdir/add_student_schema.ldif")

    print("Adding organizational units")
    for ou in ['Students', 'Praktikum']:
        filename = 'tmpdir/add_{}_org_unit.ldif'.format(ou)
        format_dict = {'ou': ou, 'in_ou_complete': ''}
        create_ldif('organizational_unit', format_dict, filename)
        add_ldif(filename)
    for i in range(1, 12):
        filename = 'tmpdir/add_Praktikum_Team{}_org_unit.ldif'.format(i)
        format_dict = {'ou': 'Team' + str(i),
                       'in_ou_complete': 'ou=Praktikum,'}
        create_ldif('organizational_unit', format_dict, filename)
        add_ldif(filename)
