import re
from datetime import datetime

from utils.constants import BIRTHDAY_DATE_FORMAT


def is_valid_date(date_str):
    date_pattern = re.compile(r'^\d{4}-\d{1,2}-\d{1,2}$')

    if not date_pattern.match(date_str):
        return False

    try:
        date_obj = datetime.strptime(date_str, BIRTHDAY_DATE_FORMAT)
        return True
    except ValueError:
        return False


if __name__ == '__main__':

    test_dates = ["1985-09-14", "1985-9-14", "1985-9-4", "2020-12-31", "2020-01-32", "2021-02-29", "2000-05-05"]

    for date in test_dates:
        print(f"{date}: {is_valid_date(date)}")
