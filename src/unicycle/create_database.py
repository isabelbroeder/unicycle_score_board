import string

import pandas as pd

from pandas import DataFrame

from src.unicycle.constants import *
from src.unicycle.db_handler.points_db_handler import PointsDbHandler
from src.unicycle.db_handler.riders_db_handler import RidersDbHandler
from src.unicycle.db_handler.routines_db_handler import RoutinesDbHandler
from src.unicycle.db_handler.riders_routines_db_handler import RidersRoutinesDbHandler

SHEET_NAME_REGISTRATION_DATA = "Teilnehmer"
SHEET_NAME_REGISTRATION_OVERVIEW = "Allg. Daten"
CELL_WITH_CLUB = (7, "E")

COL_NAMES_REGISTRATION_FILE = [
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


def read_registration_file(path: Path) -> pd.DataFrame:
    """
    Read the registration file
    Keyword arguments:
        path -- path to registration file
    return pd.Dataframe with registration data
    """

    registration = pd.read_excel(
        path, sheet_name=SHEET_NAME_REGISTRATION_DATA, skiprows=4
    )
    registration.columns = COL_NAMES_REGISTRATION_FILE

    registration = registration[registration[COL_NAMES_REGISTRATION_FILE[0]].notna()]
    registration = registration.drop(columns="entry_fee")
    registration = registration.convert_dtypes()
    registration["date_of_birth"] = registration["date_of_birth"].dt.date

    registration_overview = pd.read_excel(
        path, sheet_name=SHEET_NAME_REGISTRATION_OVERVIEW, header=None
    )
    club = registration_overview.loc[
        CELL_WITH_CLUB[0] - 1, list(string.ascii_uppercase).index(CELL_WITH_CLUB[1])
    ]
    number_of_riders = registration["name"].size
    registration.insert(4, "club", [club] * number_of_riders)

    registration_stripped = registration.map(
        lambda x: x.strip() if isinstance(x, str) else x
    )
    return registration_stripped


def fill_database_riders(
    registration: pd.DataFrame, rider_db_handler=RidersDbHandler()
):
    """
    create the database riders.db and insert registration data
    Keyword arguments:
        registration: dataframe with registration data
        rider_db_handler:
    """

    df_riders = registration[["name", "gender", "date_of_birth", "age", "club"]]
    df_riders.assign(
        age=df_riders["date_of_birth"].apply(
            lambda date_of_birth: calculate_age(date_of_birth, DATE_COMPETITION)
        )
    )
    sql_insert = """INSERT INTO riders (name, gender, date_of_birth, age_competition_day, club) VALUES (? , ? , ? , ? , ?) """
    rider_db_handler.execute(sql_insert, df_riders.itertuples(index=False, name=None))


def fill_database_routines(
    registration: pd.DataFrame,
    riders_db_handler=RidersDbHandler(),
    routines_db_handler=RoutinesDbHandler(),
    riders_routines_db_handler=RidersRoutinesDbHandler(),
):
    """
    create the databases routines.db and riders_routines.db
    Keyword arguments:
        registration: dataframe with registration data
    """

    for category in Categories:
        for age_group in set(
            registration["age_group_" + str(category)].dropna()
        ):  # age groups in this category
            for routine_name in set(
                (
                    registration[str("name_" + category)].where(
                        registration[str("age_group_" + category)] == age_group
                    )
                ).dropna()
            ):
                if routine_name.isspace():
                    continue

                sql_insert = """INSERT INTO routines (routine_name, category, age_group) VALUES (? , ? , ? )"""
                data = (
                    (
                        routine_name,
                        category,
                        age_group,
                    ),
                )
                routines_db_handler.execute(sql_insert, data)
                id_routine = routines_db_handler.cursor.lastrowid

                name_riders = (
                    registration[["name", "date_of_birth"]]
                    .where(
                        (registration[str("name_" + category)] == routine_name)
                        & (registration[str("age_group_" + category)] == age_group)
                    )
                    .dropna()
                )

                placeholders = ", ".join(["?"] * len(name_riders))
                sql_select_id_rider = f"""
                        SELECT id_rider FROM riders
                        WHERE name IN ({placeholders})
                          AND date_of_birth IN ({placeholders})
                        """

                id_rider = riders_db_handler.get_data(
                    sql_select_id_rider,
                    name_riders["name"].tolist()
                    + name_riders["date_of_birth"].tolist(),
                )

                sql_insert = """INSERT INTO riders_routines (id_rider, id_routine) VALUES (?, ? ) """

                data = list(
                    zip(
                        id_rider["id_rider"].tolist(),
                        [
                            id_routine,
                        ]
                        * len(id_rider["id_rider"].tolist()),
                    )
                )
                riders_routines_db_handler.execute(sql_insert, data)


def create_database_points(
    routines_db_handler: RoutinesDbHandler = RoutinesDbHandler(),
    points_db_handler: PointsDbHandler = PointsDbHandler(),
):
    """
    Insert keys/id of routine in database points.
    Keyword arguments:
        routines_db_handler -- DbHandler for Database with routine data
        points_db_handler -- DbHandler for Database with points
    """

    id_routine = routines_db_handler.get_data("""SELECT id_routine FROM routines""")
    id_routine_str = [f"({val})" for val in id_routine["id_routine"].values]
    id_routine_str = ", ".join(id_routine_str)
    sql_insert_keys = f"INSERT INTO points (id_routine) VALUES {id_routine_str};"
    points_db_handler.execute(sql_insert_keys)


def split_individual_male_female(
    riders_db_handler: RidersDbHandler = RidersDbHandler(),
    routines_db_handler: RoutinesDbHandler = RoutinesDbHandler(),
    riders_routines_db_handler: RidersRoutinesDbHandler = RidersRoutinesDbHandler(),
):
    """
    split the category individual into individual female and individual male
    Keyword arguments:
        riders_db_handler -- DbHandler for Database with rider data
        routines_db_handler -- DbHandler for Database with routine data
        riders_routines_db_handler -- DbHandler for Database with rider routine combination
    """

    df_riders = riders_db_handler.get_data("""SELECT id_rider, gender FROM riders""")
    df_routines = routines_db_handler.get_data(
        """SELECT id_routine, category FROM routines WHERE category == 'individual'"""
    )
    df_riders_routines = riders_routines_db_handler.get_data()

    df_individual = df_riders_routines.merge(
        df_riders, on="id_rider", how="left"
    ).merge(df_routines, on="id_routine", how="right")

    df_individual["category"] = df_individual["category"].where(
        df_individual["gender"] != "m", "individual male"
    )

    df_individual["category"] = df_individual["category"].where(
        df_individual["gender"] != "w", "individual female"
    )

    routines_db_handler.update_multiple_rows(
        df_individual, ["id_routine"], ["category"]
    )


def check_age_groups(
    age_groups: dict,
    riders_db_handler=RidersDbHandler(),
    routines_db_handler=RoutinesDbHandler(),
    riders_routines_db_handler=RidersRoutinesDbHandler(),
):
    """
    Checks for all routines whether the age groups in the registration file are correct.
    If not the age group will be corrected.
    Keyword arguments:
        age_groups -- dictionary with age groups for each category
        riders_db_handler -- DbHandler for Database with rider data
        routines_db_handler -- DbHandler for Database with routine data
        riders_routines_db_handler -- DbHandler for Database with rider routine combination

    """

    df_routines = routines_db_handler.get_data(
        """SELECT id_routine, category, age_group FROM routines"""
    )
    df_riders = riders_db_handler.get_data(
        """SELECT id_rider, age_competition_day FROM riders"""
    )
    df_riders_routines = riders_routines_db_handler.get_data()

    df = df_riders_routines.merge(df_riders, on="id_rider", how="left").merge(
        df_routines, on="id_routine", how="left"
    )

    df_max = df.groupby(["id_routine"]).max()
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
        routines_db_handler.update_multiple_rows(
            df_update_age_groups, ["id_routine"], ["age_group"]
        )


def set_age_group(age: int, age_groups: list) -> str:
    """
    Assigns correct age group to the routine.
    Keyword arguments:
        age: age of the oldest rider in this routine
        age_groups: age group in this category
    """
    age_group_routine = age_groups[0]
    for age_group in age_groups:
        if age_group[0] == "U" and int(age_group[1:]) > age:
            return age_group
        elif age_group[-1] == "+" and int(age_group[:-1]) <= age:
            return age_group
    return age_group_routine


def create_starting_order(
    age_groups: dict,
    riders_db_handler: RidersDbHandler = RidersDbHandler(),
    routines_db_handler: RoutinesDbHandler = RoutinesDbHandler(),
    riders_routines_db_handler: RidersRoutinesDbHandler = RidersRoutinesDbHandler(),
):
    """
    Creates an Excel file with the starting order
    Keyword arguments:
        age_groups -- dictionary with age groups for all categories
        riders_db_handler -- DbHandler for Database with rider data
        routines_db_handler -- DbHandler for Database with routine data
        riders_routines_db_handler -- DbHandler for Database with rider routine combination
    """
    df_riders = riders_db_handler.get_data(
        """SELECT id_rider, name, club FROM riders"""
    )
    df_routines = routines_db_handler.get_data(
        """SELECT id_routine, routine_name, category, age_group FROM routines"""
    )
    df_riders_routines = riders_routines_db_handler.get_data()
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

    with pd.ExcelWriter(
        Path(get_path_project_root(), "output/starting_order.xlsx"), engine="openpyxl"
    ) as writer:
        empty_df = DataFrame()
        empty_df.to_excel(writer, sheet_name="Tabelle1")
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


def calculate_age(date_of_birth: datetime, date: datetime = None) -> int:
    """
    Calculate the age at a given date or today if not specified.
    Keyword arguments:
        date_of_birth -- The date of birth as a datetime object.
        date -- The date on which to calculate the age. Defaults to today if not provided.
    return -- The age in years.
    """
    if date is None:
        date = datetime.today()
    age = date.year - date_of_birth.year
    if date_of_birth.month > date.month or (
        date_of_birth.month == date.month and date_of_birth.day > date.day
    ):  # had not yet had their birthday that year
        return age - 1
    return int(age)


def replace_single_element(s):
    """
    Replaces a set with a single element with that element.
    s: set or any other data type
    return: single item of a set or s
    """
    if isinstance(s, set) and len(s) == 1:
        return s.pop()
    else:
        return s


def format_names(names):
    """
    Formats a set of names or drivers into a readable string.
    Keyword arguments:
        s (set or any): A set of names or other data.

    Returns:
        str or original type:
            - If s is a set with exactly two elements, returns a string with both names separated by 'und'.
            - If s has more than two elements, returns a string indicating the number of riders.
            - Otherwise, returns the input as-is.
    """
    if isinstance(names, set):
        if len(names) == 2:
            return f"{names.pop()} und {names.pop()}"
        if len(names) > 2:
            return f"{len(names)} Fahrer/innen"
    else:
        return names


def main():
    """
    Creates Databases for riders, routines, the combination of riders and routines, and points from the registrationfiles.
    Creates starting order.
    """
    registration_files = Path(get_path_project_root(), "data/registration_files").glob(
        "*.xlsx"
    )
    riders_db_handler = RidersDbHandler()
    routines_db_handler = RoutinesDbHandler()
    riders_routines_db_handler = RidersRoutinesDbHandler()
    points_db_handler = PointsDbHandler()

    riders_db_handler.create_table()
    routines_db_handler.create_table()
    riders_routines_db_handler.create_table()
    points_db_handler.create_table()

    for file in registration_files:
        registration = read_registration_file(path=Path(get_path_project_root(), file))
        fill_database_riders(registration)
        fill_database_routines(registration)
    create_database_points(routines_db_handler, points_db_handler)
    split_individual_male_female()

    check_age_groups(AGE_GROUPS)
    create_starting_order(AGE_GROUPS)

    riders_routines_db_handler.disconnect()
    riders_db_handler.disconnect()
    routines_db_handler.disconnect()
    points_db_handler.disconnect()


if __name__ == "__main__":
    main()
