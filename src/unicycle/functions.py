"""calculates ages for different routine groups"""

import datetime

import pandas as pd

from src.unicycle.load_data import DataLoader


def calculate_age(date_of_birth: datetime, date: datetime) -> int:
    """
    calculate the age at a given date
    """
    age = date.year - date_of_birth.year
    if date_of_birth.month > date.month or (
        date_of_birth.month == date.month and date_of_birth.day > date.day
    ):  # had not yet had their birthday that year
        return age - 1
    return age


def main():
    print(calculate_age(datetime.datetime(2002, 12, 4), datetime.datetime(2025, 3, 23)))


if __name__ == "__main__":
    main()
