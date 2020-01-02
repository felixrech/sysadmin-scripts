from common import cleanup
from setup_ldap import setup
from setup_users import add_existing_users, add_new_users

if input("Do you need to setup LDAP? y/N ") == 'y':
    setup()
if input("Do you want to add users? y/N ") == 'y':
    add_existing_users()
    add_new_users()
if input("Delete temporary data? y/N ") == 'y':
    cleanup()
