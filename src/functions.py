""" calculates ages for different routine groups """


import datetime
import sqlite3

import pandas as pd

from load_data import DataLoader



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


def calculate_results(category: str, age_group: str) -> pd.DataFrame:
    #df_routines = DataLoader("../data/routines.db", "routines").get_data()
    df_points = DataLoader("../data/points.db", "points").get_data("SELECT *' FROM points WHERE age_group = ? AND category = ?", [age_group, category])

    #connection_points = sqlite3.connect("../data/points.db")
    #cursor_points = connection_points.cursor()
    #df_points = cursor_points.execute(
    #    "SELECT * FROM points WHERE age_group = ? AND category = ?",
    #    (age_group, category)
    #).fetchall()
    print(df_points)


def main():
    #print(calculate_age(datetime.datetime(2002, 12, 4), datetime.datetime(2025, 3, 23)))
    calculate_results('individual', 'U21')

if __name__ == "__main__":
    main()

