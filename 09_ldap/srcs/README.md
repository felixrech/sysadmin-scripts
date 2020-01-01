# LDAP setup script

This script will help you install/configure some parts of the LDAP setup. This includes the creation of organizational units and schemas for the user management and a way to import both existing and new users.

## Requirements

- First of all, this script requires Python in version 3.7 or higher and the pip utility (or another way to install python packages):

    ```bash
    apt install python3.7 python3-pip
    ```

- Install the `unidecode` python package which is used to filter out Umlaute and the likes from last names when creating usernames:

    ```bash
    python3.7 -m pip install Unidecode
    ```

- Additional files: The script expects some files to present. In case your file format or naming varies, convert your files to the format present or have a look at `setup_users.py` - making the changes necessary shouldn't be too hard!
    1. A json file called `srcs/existing_users.json` with the existing users of the following format:

        ```json
        [
            {
                "username": "doe",
                "uid": 10001,
                "team": 1,
                "first_name": "John",
                "last_name": "Doe"
            }
        ]
        ```
    
    2. A csv file with new users in `srcs/student.csv`. As the file provided by the practical course was in German, the header line has been left untranslated:

        ```csv
        "Name","Vorname","Geschlecht","Geburtsdatum","Geburtsort","Nationalität","Straße","PLZ","Ort","Telefon","Matrikelnummer"
        Doe,John,m,1.1.70,Los Angeles,US,Nice Street,12345,Washington DC,1234/1234,123456
        Doe,Jane,f,6.6.76,Toronto,CA,Nice Street,12345,Washington DC,1234/1235,123457
        ```

        A translation of the header column would be:
        ```csv
        "Last Name","First Name","Gender","Date of birth","Place of birth","Nationality","Address","Zip code","City","Phone Nr.","Student number"
        ```

## Usage

Usage is as easy as executing the `main.py` file:

```bash
root@ldap-vm$ python3.7 main.py
Do you need to setup LDAP? y/N y
...
```