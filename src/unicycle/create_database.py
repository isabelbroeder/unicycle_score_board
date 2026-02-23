import datetime
import sqlite3

import pandas
import pandas as pd
import os

from pandas import DataFrame


from src.unicycle.functions import calculate_age
from pathlib import Path

from src.unicycle.load_data import DataLoader

DATE_COMPETITION = datetime.datetime(2026, 3, 7, 0, 0)
CATEGORIES = ["individual", "pair", "small_group", "large_group"]


def read_registration_file(path: Path, club: str) -> pandas.DataFrame:
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

    registration["date_of_birth"] = registration["date_of_birth"].dt.date

    # Add club
    number_of_riders = registration["name"].size
    registration.insert(4, "club", [club] * number_of_riders)
    registration_stripped = registration.map(
        lambda x: x.strip() if isinstance(x, str) else x
    )
    return registration_stripped


def create_database_riders(registration: pd.DataFrame):
    """
    create the database riders.db
    Keyword arguments:
        registration: dataframe with registration data
    """

    # connect to database
    script_dir = os.path.dirname(os.path.abspath(__file__))
    unicycle_score_board_path = Path(script_dir).parent.parent
    connection = sqlite3.connect(Path(unicycle_score_board_path, "data/riders.db"))
    cursor = connection.cursor()
    sqlite3.register_adapter(datetime.date, adapt_date_iso)
    sqlite3.register_converter("date", convert_date)

    # create new database
    # cursor.execute("DROP TABLE IF EXISTS riders")
    sql_create_table = """
        CREATE TABLE IF NOT EXISTS riders (
        id_rider INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(50),
        gender CHAR(1),
        date_of_birth DATE,
        age_competition_day INTEGER,
        club VARCHAR(50));"""
    cursor.execute(sql_create_table)
    connection.commit()

    # insert riders into database riders
    df_riders = registration[["name", "date_of_birth", "age", "gender", "club"]]
    for row in range(0, len(registration)):
        age = calculate_age(df_riders["date_of_birth"][row], DATE_COMPETITION)
        sql_insert = """INSERT INTO riders (name, gender, date_of_birth, age_competition_day, club) VALUES (? , ? , ? , ? , ?) """
        data = (
            df_riders["name"][row],
            df_riders["gender"][row],
            df_riders["date_of_birth"][row],
            age,
            df_riders["club"][row],
        )
        cursor.execute(sql_insert, data)
        id_rider = cursor.lastrowid
    connection.commit()
    connection.close()


def create_database_routines(registration: pd.DataFrame):
    """
    create the databases routines.db and riders_routines.db
    Keyword arguments:
        registration: dataframe with registration data
    """

    # connect to database routines
    script_dir = os.path.dirname(os.path.abspath(__file__))
    unicycle_score_board_path = Path(script_dir).parent.parent
    connection_routines = sqlite3.connect(
        Path(unicycle_score_board_path, "data/routines.db")
    )
    cursor_routines = connection_routines.cursor()

    # create new database routines
    # cursor_routines.execute("DROP TABLE IF EXISTS routines")
    sql_create = """
    CREATE TABLE IF NOT EXISTS routines (
    id_routine INTEGER PRIMARY KEY AUTOINCREMENT,
    routine_name VARCHAR(50),
    category VARCHAR(20),
    age_group VARCHAR(20));"""
    cursor_routines.execute(sql_create)
    connection_routines.commit()

    # connect to database riders_routines
    connection_riders_routines = sqlite3.connect(
        Path(unicycle_score_board_path, "data/riders_routines.db")
    )
    cursor_riders_routines = connection_riders_routines.cursor()

    # create new database riders_routines
    # cursor_riders_routines.execute("DROP TABLE IF EXISTS riders_routines")
    sql_create = """
        CREATE TABLE IF NOT EXISTS riders_routines (
        id_rider INTEGER,
        id_routine INTEGER,
        PRIMARY KEY (id_rider, id_routine));"""
    cursor_riders_routines.execute(sql_create)
    connection_riders_routines.commit()

    # connect to database riders
    connection_riders = sqlite3.connect(
        Path(unicycle_score_board_path, "data/riders.db")
    )
    cursor_riders = connection_riders.cursor()

    for category in CATEGORIES:
        for age_group in set(
            registration["age_group_" + str(category)].dropna()
        ):  # age groups in this category
            for routine_name in set(
                (
                    registration[str("name_" + category)].where(
                        registration[str("age_group_" + category)] == age_group
                    )
                ).dropna()  # routine names in this category and age group
            ):
                if routine_name.isspace():
                    continue

                sql_insert = """INSERT INTO routines (routine_name, category, age_group) VALUES (? , ? , ? )"""
                data = (
                    routine_name,
                    category,
                    age_group,
                )

                cursor_routines.execute(sql_insert, data)
                connection_routines.commit()
                id_routine = cursor_routines.lastrowid

                # get riders of routine
                name_riders = (
                    registration[["name", "date_of_birth"]]
                    .where(
                        (registration[str("name_" + category)] == routine_name)
                        & (registration[str("age_group_" + category)] == age_group)
                    )
                    .dropna()
                )
                sql_select_id_rider = """SELECT id_rider FROM riders WHERE name == ? AND date_of_birth == ?"""
                # name_riders = name_riders.reset_index()
                for index, row in name_riders.iterrows():
                    id_rider = cursor_riders.execute(
                        sql_select_id_rider, (row["name"], row["date_of_birth"])
                    ).fetchone()[0]

                    sql_insert = """INSERT INTO riders_routines (id_rider, id_routine) VALUES (?, ? ) """
                    data = (
                        id_rider,
                        id_routine,
                    )
                    cursor_riders_routines.execute(sql_insert, data)

    connection_riders_routines.commit()
    connection_riders_routines.close()
    connection_routines.close()
    connection_riders.close()


def split_individual_male_female():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    unicycle_score_board_path = Path(script_dir).parent.parent

    dataloader_routines = DataLoader(
        Path(unicycle_score_board_path, "data/routines.db"), "routines"
    )
    df_routines = dataloader_routines.get_data(
        """SELECT id_routine, category FROM routines WHERE category == 'individual'"""
    )
    df_riders = DataLoader(
        Path(unicycle_score_board_path, "data/riders.db"), "riders"
    ).get_data("""SELECT id_rider, gender FROM riders""")
    df_riders_routines = DataLoader(
        Path(unicycle_score_board_path, "data/riders_routines.db"), "riders_routines"
    ).get_data()

    df_individual = df_riders_routines.merge(
        df_riders, on="id_rider", how="left"
    ).merge(df_routines, on="id_routine", how="right")
    df_individual["category"] = df_individual["category"].where(
        df_individual["gender"] != "m", "individual male"
    )
    df_individual["category"] = df_individual["category"].where(
        df_individual["gender"] != "w", "individual female"
    )

    dataloader_routines.update_multiple_rows(
        df_individual, ["id_routine"], ["category"]
    )


def check_age_groups(age_groups: dict):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    unicycle_score_board_path = Path(script_dir).parent.parent

    dataloader_routines = DataLoader(
        Path(unicycle_score_board_path, "data/routines.db"), "routines"
    )
    df_routines = dataloader_routines.get_data(
        """SELECT id_routine, category, age_group FROM routines"""
    )
    df_riders = DataLoader(
        Path(unicycle_score_board_path, "data/riders.db"), "riders"
    ).get_data("""SELECT id_rider, age_competition_day FROM riders""")
    df_riders_routines = DataLoader(
        Path(unicycle_score_board_path, "data/riders_routines.db"), "riders_routines"
    ).get_data()
    df = df_riders_routines.merge(df_riders, on="id_rider", how="left").merge(
        df_routines, on="id_routine", how="right"
    )

    df_max = df.groupby(["id_routine"]).max()
    print(df_max)
    df_update_age_groups = DataFrame(columns=["id_routine", "age_group"])

    for row in range(df_routines.shape[0]):
        age_group_routine = set_age_group(
            df_max["age_competition_day"].iloc[row],
            age_groups[df_max["category"].iloc[row]],
        )
        if age_group_routine != df_max["age_group"].iloc[row]:
            new_row = pd.DataFrame(
                {"id_routine": df_max.index[row], "age_group": age_group_routine},
                index=[0],
            )
            df_update_age_groups = pd.concat(
                [new_row, df_update_age_groups.loc[:]]
            ).reset_index(drop=True)
            print(
                "INFO: the age group of routine",
                df_max.index[row],
                " was corrected from ",
                df_max["age_group"].iloc[row],
                " to ",
                age_group_routine,
            )

    if not df_update_age_groups.empty:
        dataloader_routines.update_multiple_rows(
            df_update_age_groups, ["id_routine"], ["age_group"]
        )


def set_age_group(age: int, age_groups: list) -> str:
    """
    assigns routine to the correct age group
    age: age of the oldest rider in this routine
    age_groups: age_groups in this category
    """
    age_group_routine = age_groups[0]
    for age_group in age_groups:
        if age_group[0] == "U" and int(age_group[1:]) > age:
            # age_group_routine = age_group
            return age_group
        elif age_group[-1] == "+" and int(age_group[:-1]) <= age:
            return age_group
    return age_group_routine


def create_starting_order(age_groups):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    unicycle_score_board_path = Path(script_dir).parent.parent

    # dataloader_routines = DataLoader(Path(unicycle_score_board_path, "data/routines.db"), "routines")

    df_routines = DataLoader(
        Path(unicycle_score_board_path, "data/routines.db"), "routines"
    ).get_data("""SELECT id_routine, routine_name, category, age_group FROM routines""")
    df_riders = DataLoader(
        Path(unicycle_score_board_path, "data/riders.db"), "riders"
    ).get_data("""SELECT id_rider, name, club FROM riders""")
    df_riders_routines = DataLoader(
        Path(unicycle_score_board_path, "data/riders_routines.db"), "riders_routines"
    ).get_data()
    df = df_riders_routines.merge(df_riders, on="id_rider", how="left").merge(
        df_routines, on="id_routine", how="left"
    )
    df = df.groupby("id_routine").agg(lambda x: set(x))
    df = df.map(replace_single_element)
    df.category = pd.Categorical(
        df.category,
        categories=[
            "individual male",
            "individual female",
            "pair",
            "small_group",
            "large_group",
        ],
    )
    df = df.sample(frac=1)
    df = df.sort_values(["category", "age_group"], ascending=[True, False])
    df["name"] = df["name"].apply(lambda x: format_names(x))
    df = df[["routine_name", "name", "club", "category", "age_group"]]


    with pd.ExcelWriter("output.xlsx", engine="openpyxl") as writer:
        # df.to_excel(writer, index=False, startrow=1, startcol=0)
        empty_df = DataFrame()
        empty_df.to_excel(writer, sheet_name="Tabelle1")
        workbook = writer.book
        worksheet = writer.sheets["Tabelle1"]
        max_row = 1
        for category, list_age_group in age_groups.items():
            for age_group in list_age_group:
                df1 = df[(df["category"] == category) & (df["age_group"] == age_group)]
                worksheet.merge_cells(f"A{max_row}:C{max_row}")
                worksheet[f"A{max_row}"] = f"{category} {age_group}"
                df1[["routine_name", "name", "club"]].to_excel(
                    writer,
                    sheet_name="Tabelle1",
                    index=False,
                    startrow=max_row,
                    header=False,
                )
                max_row = max_row + len(df1) + 1


def get_maximum_rows(sheet_object):
    count = 0
    for row in sheet_object:
        if not all([(cell.value is None or cell.value == "") for cell in row]):
            count += 1

    return count


def replace_single_element(s):
    if isinstance(s, set) and len(s) == 1:
        return next(iter(s))
    else:
        return s


def format_names(s):
    if isinstance(s, set):
        if len(s) == 2:
            return f"{s.pop()} und {s.pop()}"
        if len(s) > 2:
            return f"{len(s)} Fahrer/innen"
    else:
        return s


def adapt_date_iso(val):
    """Adapt datetime.date to ISO 8601 date."""
    return val.isoformat()


def convert_date(val):
    """Convert ISO 8601 date to datetime.date object."""
    return datetime.date.fromisoformat(val.decode())


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    unicycle_score_board_path = Path(script_dir).parent.parent
    registration_files = DataFrame(
        {
            "club": ["SV Schlumpfhausen", "TSV Lummerland", "SV Entenhausen"],
            "path": [
                "data/Anmeldung_Landesmeisterschaft_2025_Verein1.xlsx",
                "data/Anmeldung_Landesmeisterschaft_2025_Verein2.xlsx",
                "data/Anmeldung_Landesmeisterschaft_2025_Verein3.xlsx",
            ],
        }
    )

    for index, row in registration_files.iterrows():
        registration = read_registration_file(
            path=Path(unicycle_score_board_path, row["path"]),
            club=row["club"],
        )
        create_database_riders(registration)

        create_database_routines(registration)

    split_individual_male_female()

    age_groups = {
        "individual male": ["U9", "U11", "U13", "U15", "U30", "30+"],
        "individual female": ["U9","U11", "U12", "U13", "U15", "U17", "U30", "30+"],
        "pair": ["U9","U11", "U12", "U13", "U15", "U30", "30+"],
        "small_group": ["U11", "U13","U15", "15+"],
        "large_group": ["U12", "12+"],
    }
    check_age_groups(age_groups)
    create_starting_order(age_groups)


if __name__ == "__main__":
    main()
