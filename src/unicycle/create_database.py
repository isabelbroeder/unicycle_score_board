import datetime
import sqlite3

import pandas
import pandas as pd

from functions import calculate_age

WETTKAMPFTAG = datetime.datetime(2025, 5, 1, 0, 0)
CATEGORIES = ["individual", "pair", "small_group", "large_group"]


def read_registration_file(path: str, club: str) -> pandas.DataFrame:
    """
    Read the registration file
    Keyword arguments:
        path -- path to registration file
        club -- club whose registration file is read in
    return pandas.Dataframe with registration data
    """
    # read registration file
    registration = pd.read_excel(path, sheet_name=1, skiprows=4)
    registration.columns = [
        "name",
        "date_of_birth",
        "age",
        "gender",
        "start_individual",
        "name_individual",
        "age_group_individual",
        "start_pair",
        "name_pair",
        "age_group_pair",
        "start_small_group",
        "name_small_group",
        "age_group_small_group",
        "start_large_group",
        "name_large_group",
        "age_group_large_group",
        "entry_fee",
    ]
    registration = registration[registration["name"].notna()]  # only rows with entries
    registration = registration.drop(columns="entry_fee")
    registration = registration.convert_dtypes()

    # Add club
    number_of_riders = registration["name"].size
    registration.insert(4, "club", [club] * number_of_riders)
    # print("registration.columns", registration.columns)
    return registration


def create_database_riders(registration: pd.DataFrame):
    """
    create the database riders.db
    Keyword arguments:
        registration: dataframe with registration data
    """
    # connect to database
    connection = sqlite3.connect("../../data/riders.db")
    cursor = connection.cursor()
    df_riders = registration[["name", "date_of_birth", "age", "gender", "club"]]
    # df_riders.to_sql('fahrerinnen', connection, if_exists = 'append')
    cursor.execute("DROP TABLE IF EXISTS riders")
    sql_erstellen = """
        CREATE TABLE riders (
        id_rider INTEGER PRIMARY KEY,
        name VARCHAR(50),
        gender CHAR(1),
        date_of_birth DATE,
        age_competition_day INTEGER,
        club VARCHAR(50));"""
    cursor.execute(sql_erstellen)
    for row in range(0, len(registration)):
        age = calculate_age(
            df_riders["date_of_birth"][row].to_pydatetime(), WETTKAMPFTAG
        )
        sql_insert = """INSERT INTO riders (id_rider, name, gender, date_of_birth, age_competition_day, club) VALUES (?, ? , ? , ? , ? , ?) """
        data = (
            None,
            df_riders["name"][row],
            df_riders["gender"][row],
            df_riders["date_of_birth"][row].strftime("%Y-%m-%d"),
            age,
            df_riders["club"][row],
        )
        cursor.execute(sql_insert, data)
        connection.commit()


def create_database_routines(registration: pd.DataFrame):
    """
    create the databases routines.db and riders_routines.db
    Keyword arguments:
        registration: dataframe with registration data
    """
    # create_database_routines
    connection_routines = sqlite3.connect("../../data/routines.db")
    cursor_routines = connection_routines.cursor()
    cursor_routines.execute("DROP TABLE IF EXISTS routines")
    sql_create = """
    CREATE TABLE routines (
    id_routine INTEGER PRIMARY KEY,
    routine_name VARCHAR(50),
    category VARCHAR(20),
    age_group VARCHAR(20));"""
    cursor_routines.execute(sql_create)
    connection_routines.commit()

    # create_database_riders_routines
    connection_riders_routines = sqlite3.connect("../../data/riders_routines.db")
    cursor_riders_routines = connection_riders_routines.cursor()
    cursor_riders_routines.execute("DROP TABLE IF EXISTS riders_routines")
    sql_create = """
        CREATE TABLE riders_routines (
        id_rider INTEGER,
        id_routine INTEGER,
        PRIMARY KEY (id_rider, id_routine));"""
    cursor_riders_routines.execute(sql_create)
    connection_riders_routines.commit()

    connection_riders = sqlite3.connect("../../data/riders.db")
    cursor_riders = connection_riders.cursor()

    sql_select_max_id = """SELECT MAX(id_routine) FROM routines"""
    id_routine = cursor_routines.execute(sql_select_max_id).fetchone()[0]
    print(id_routine)
    if id_routine == None:
        id_routine = 0

    for category in CATEGORIES:
        for age_group in set(registration["age_group_" + str(category)].dropna()): #age groups in this category
            # print(category, age_group)
            # print(registration[str("age_group_" + category)])
            for routine_name in set(
                (
                    registration[str("name_" + category)].where(
                        registration[str("age_group_" + category)] == age_group
                    )
                ).dropna() # routine names in this category and age group
            ):
                if routine_name.isspace():
                    continue
                id_routine += 1
                # print(routine_name)

                sql_insert = """INSERT INTO routines (id_routine, routine_name, category, age_group) VALUES (?, ? , ? , ? ) """
                data = (
                    id_routine,
                    routine_name,
                    category,
                    age_group,
                )
                print(id_routine, routine_name)
                cursor_routines.execute(sql_insert, data)
                connection_routines.commit()

                name_riders = (
                    registration["name"]
                    .where(
                        (registration[str("name_" + category)] == routine_name)
                        & (registration[str("age_group_" + category)] == age_group)
                    )
                    .dropna()
                )
                sql_select_id_rider = """SELECT id_rider FROM riders WHERE name == ?"""
                # name_rider = str(name_rider)
                # print(len(name_riders))
                for name_rider in name_riders:
                    id_rider = cursor_riders.execute(
                        sql_select_id_rider, (name_rider,)
                    ).fetchone()[0]
                    print(id_rider, name_rider)

                    sql_insert = """INSERT INTO riders_routines (id_rider, id_routine) VALUES (?, ? ) """
                    data = (
                        id_rider,
                        id_routine,
                    )
                    cursor_riders_routines.execute(sql_insert, data)
                    connection_riders_routines.commit()


def main():
    registration = read_registration_file(
        path="../../data/Anmeldung_Landesmeisterschaft_2025.xlsx", club="BW96_Schenefeld"
    )
    create_database_riders(registration)

    create_database_routines(registration)


if __name__ == "__main__":
    main()

# print(registration)


