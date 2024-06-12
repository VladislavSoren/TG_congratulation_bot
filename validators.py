import re
from datetime import datetime


def is_valid_date(date_str):
    date_pattern = re.compile(r'^\d{1,2}\.\d{1,2}\.\d{4}$')

    if not date_pattern.match(date_str):
        return False

    try:
        date_obj = datetime.strptime(date_str, '%d.%m.%Y')
        return True
    except ValueError:
        return False


if __name__ == '__main__':

    test_dates = ["14.09.1985", "14.9.1985", "4.9.1985", "31.12.2020", "32.01.2020", "29.02.2021", "29.02.2020"]

    for date in test_dates:
        print(f"{date}: {is_valid_date(date)}")
