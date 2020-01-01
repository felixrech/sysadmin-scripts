from setup_ldap import setup
from setup_users import add_existing_users, add_new_users

if input("Do you need to setup LDAP? y/N ") == 'y':
    setup()
add_existing_users()
add_new_users()
