import datetime
import sqlite3
from enum import StrEnum

import pandas
import pandas as pd

from functions import calculate_age
from pathlib import Path

WETTKAMPFTAG = datetime.datetime(2025, 5, 1)  # Stay in english in code. This avoids mixing up languages which is hard for every reader coming from either language
# COMPETITION_DAY = datetime.date(2025, 5, 1)  # use appropriate data type. If you don't need time information, just use date :)
CATEGORIES = ["individual", "pair", "small_group", "large_group"]  # if you use a distinct set of options, usually an Enum is the correct data type. See example below.

# class Categories(StrEnum):
#     INDIVIDUAL = "individual"
#     PAIR = "pair"
#     SMALL_GROUP = "small_group"
#     LARGE_GROUP = "large_group"


QUERY_INSERT_ROUTINES_TEMPLATE = "INSERT INTO routines (routine_name, category, age_group) VALUES (?, ?, ?)"

def read_registration_file(path: Path, club: str) -> pandas.DataFrame:
    """
    Read the registration file
    Keyword arguments:
        path -- path to registration file
        club -- club whose registration file is read in
    return pandas.Dataframe with registration data
    """
    # Nice docstring. There a dedicated styles for it maybe checkout "restructured Text" or "Numpy". You can even set this up in PyCharm

    # read registration file  # unnecessary comment, the function name is sufficient. Keep comments as minimal as possible
    registration = pd.read_excel(path, sheet_name=1, skiprows=4)
    registration.columns = [   # magic value -> constant (the list below)
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
    registration = registration[registration["name"].notna()]  # only rows with entries  # magic value -> constant
    registration = registration.drop(columns="entry_fee")  # magic value -> constant
    registration = registration.convert_dtypes()

    # Add club  # obvious comment -> remove
    number_of_riders = registration["name"].size  # magic value -> constant
    registration.insert(4, "club", [club] * number_of_riders)  # magic value -> constant
    # print("registration.columns", registration.columns)  # remove
    return registration


def create_database_riders(registration: pd.DataFrame):
    """
    create the database riders.db
    Keyword arguments:
        registration: dataframe with registration data
    """
    # This function is quite big and does alot of things. Please split this up. A good strategy wood be separate all the blocks, where you wrote a comment above it...
    # connect to database  # obvious comment -> remove
    connection = sqlite3.connect("../../data/riders.db")  # "../../data/riders.db" is a "magic value" (in code defined constant) These are dangerous if they might change. You have to adapt them everywhere you use them. Therefore it is better to define a constant which is then used by everyone. -> use same constant as in app.py.Might be defined here and imported to app.py.
    cursor = connection.cursor()

    # create new database  # obvious comment -> remove
    cursor.execute("DROP TABLE IF EXISTS riders")
    sql_erstellen = """
        CREATE TABLE riders (
        id_rider INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(50),
        gender CHAR(1),
        date_of_birth DATE,
        age_competition_day INTEGER,
        club VARCHAR(50));"""
    cursor.execute(sql_erstellen)
    connection.commit()


    # insert riders into database riders  # obvious comment -> remove
    df_riders = registration[["name", "date_of_birth", "age", "gender", "club"]]  # magic value -> constant
    for row in range(len(registration)):
        age = calculate_age(
            df_riders["date_of_birth"][row].to_pydatetime(), WETTKAMPFTAG  # magic value -> constant
        )
        sql_insert = """INSERT INTO riders (name, gender, date_of_birth, age_competition_day, club) VALUES (? , ? , ? , ? , ?) """  # make constant
        data = (
            df_riders["name"][row],  # magic value -> constant
            df_riders["gender"][row],  # magic value -> constant
            df_riders["date_of_birth"][row].strftime("%Y-%m-%d"),  # magic value -> constant, also the format should be a constant `DATE_FORMAT`
            age,
            df_riders["club"][row],  # magic value -> constant
        )
        cursor.execute(sql_insert, data)
        id_rider = cursor.lastrowid
        print('ID rider:', id_rider)
    connection.commit()
    connection.close()


def create_database_routines(registration: pd.DataFrame):
    """
    create the databases routines.db and riders_routines.db
    Keyword arguments:
        registration: dataframe with registration data
    """
    # This function is quite big and does alot of things. Please split this up. A good strategy wood be separate all the blocks, where you wrote a comment above it...
    # This one also seems to tackle two tasks: handling routines and riders_routines please
    # connect to database routines
    connection_routines = sqlite3.connect("../../data/routines.db")  # "../../data/routines.db" is a "magic value" (in code defined constant) These are dangerous if they might change. You have to adapt them everywhere you use them. Therefore it is better to define a constant which is then used by everyone. -> use same constant as in app.py.Might be defined here and imported to app.py.
    cursor_routines = connection_routines.cursor()

    # create new database routines  # obvious comment -> remove
    cursor_routines.execute("DROP TABLE IF EXISTS routines")
    sql_create = """
    CREATE TABLE routines (
    id_routine INTEGER PRIMARY KEY AUTOINCREMENT,
    routine_name VARCHAR(50),
    category VARCHAR(20),
    age_group VARCHAR(20));"""
    cursor_routines.execute(sql_create)
    connection_routines.commit()

    # connect to database riders_routines  # obvious comment -> remove
    connection_riders_routines = sqlite3.connect("../../data/riders_routines.db")  # "../../data/riders_routines.db" is a "magic value" (in code defined constant) These are dangerous if they might change. You have to adapt them everywhere you use them. Therefore it is better to define a constant which is then used by everyone. -> use same constant as in app.py.Might be defined here and imported to app.py.
    cursor_riders_routines = connection_riders_routines.cursor()

    # create new database riders_routines  # obvious comment -> remove
    cursor_riders_routines.execute("DROP TABLE IF EXISTS riders_routines")
    sql_create = """
        CREATE TABLE riders_routines (
        id_rider INTEGER,
        id_routine INTEGER,
        PRIMARY KEY (id_rider, id_routine));"""
    cursor_riders_routines.execute(sql_create)
    connection_riders_routines.commit()

    # connect to database riders
    connection_riders = sqlite3.connect("../../data/riders.db")
    cursor_riders = connection_riders.cursor()

    for category in CATEGORIES:
        for age_group in set(registration[f"age_group_{category}"].dropna()):  # age groups in this category  # unnecessary comment, please remove;   # magic value -> template-constant, AGE_GROUP_COLUMN_TEMPLATE = "age_group_{category}"; AGE_GROUP_COLUMN_TEMPLATE.format(category='...')
            print(category, age_group)  # logging is better, but it should have at least a meaningful message, so that others aren't just clueless about two values ;)
            # print(registration[str("age_group_" + category)])  # remove
            for routine_name in set(
                (
                    registration[f"name_{category}"].where(  # magic value -> template-constant, see above
                        registration[f"age_group_{category}"] == age_group  # magic value -> template-constant, see above
                    )
                ).dropna() # routine names in this category and age group  # Why is this comment on the `dropna`?
            ):
                if routine_name.isspace():
                    continue  # nice

                data = (
                    routine_name,
                    category,
                    age_group,
                )

                cursor_routines.execute(QUERY_INSERT_ROUTINES_TEMPLATE, data)
                connection_routines.commit()
                id_routine = cursor_routines.lastrowid
                print(id_routine, routine_name)

                name_riders = (
                    registration["name"]  # magic value -> constant
                    .where(
                        (registration[f"name_{category}"] == routine_name)  # magic value -> template-constant, see above
                        & (registration[f"age_group_{category}"] == age_group)  # magic value -> template-constant, see above
                    )
                    .dropna()
                )
                sql_select_id_rider = """SELECT id_rider FROM riders WHERE name == ?"""  # magic value -> query template constant, see QUERY_INSERT_ROUTINES_TEMPLATE
                # name_rider = str(name_rider)
                # print(len(name_riders))
                for name_rider in name_riders:
                    id_rider = cursor_riders.execute(
                        sql_select_id_rider, (name_rider,)
                    ).fetchone()[0]
                    print(id_rider, name_rider)  # logging is better, but it should have at least a meaningful message, so that others aren't just clueless about two values ;)

                    data = (
                        id_rider,
                        id_routine,
                    )
                    cursor_riders_routines.execute(QUERY_INSERT_ROUTINES_TEMPLATE, data)

    connection_riders_routines.commit()
    connection_riders_routines.close()
    connection_routines.close()
    connection_riders.close()


def main():
    unicycle_score_board_path = Path(Path.cwd().parent.parent)  # make data path a constant which is then reused by everyone
    registration = read_registration_file(
        path=unicycle_score_board_path / "data/Anmeldung_Landesmeisterschaft_2025.xlsx",
        club="BW96 Schenefeld",
    )
    create_database_riders(registration)

    create_database_routines(registration)


if __name__ == "__main__":
    main()

# print(registration)  # remove


