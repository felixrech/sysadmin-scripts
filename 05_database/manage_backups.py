from sys import argv
from os import listdir, remove
from datetime import datetime, timedelta

today = datetime.today()


def generate_dates():
    days = list(map(lambda i: today - timedelta(days=i), range(5000)))
    days = list(map(lambda d: datetime(*d.timetuple()[:3]), days))
    return days


def first_sunday_in_month(day):
    start_of_month = datetime(*day.timetuple()[:2] + (1,))
    for offset in range(32):
        if (start_of_month + timedelta(days=offset)).weekday() == 6:
            return start_of_month + timedelta(days=offset)


def filter_days(days):
    # Remove weekdays if from older than past two weeks
    last_sunday = next(d for d in days[14:] if d.weekday() == 6)
    days = filter(lambda d: d >= last_sunday or d.weekday() == 6, days)
    # Remove but first sunday every month if older than past year
    days = filter(lambda d: d.year >= today.year - 1
                  or d == first_sunday_in_month(d), days)
    # Remove but quarter if older than past five years
    days = filter(lambda d: d.year >= today.year - 5
                  or d.month in [1, 4, 7, 10], days)
    return list(days)


def delete_backups(days, interactive=False):
    filenames = listdir('/var/mariadb/backups/')
    allowed_filenames = list(map(lambda d: d.strftime('%Y-%m-%d.gz'), days))
    delete_filenames = set(filenames) - set(allowed_filenames)
    print("Will delete the following files:\n", delete_filenames)
    if not interactive or input('Continue? y/N ') == 'y':
        for filename in delete_filenames:
            remove('/var/mariadb/backups/' + filename)


def pprint(days, weeks=300):
    full_days = generate_dates()
    start = next(i for i, d in enumerate(days[1:]) if d.weekday() == 6)

    def print_day(day):
        if full_days[day] in days:
            print(full_days[day].strftime('%d.%m.%Y') + '\t', end='')
        else:
            print('          \t', end='')
    # Print the first week
    print('|\t', end='')
    for day in range(start, -1, -1):
        print_day(day)
    for day in range(6 - len(range(start, -1, -1))):
        print('----------\t', end='')
    print('|')
    # Print the other weeks
    for week in range(weeks-1):
        print('|\t', end='')
        for day in range(start + (week+1) * 7 - 1, start + week * 7, -1):
            print_day(day)
        print('|')


if __name__ == "__main__":
    days = filter_days(generate_dates())
    if len(argv) > 1 and argv[1] == 'print':
        pprint(filter_days(days))
    elif len(argv) > 1 and argv[1] == 'interactive':
        delete_backups(days, interactive=True)
    else:
        delete_backups(days)
