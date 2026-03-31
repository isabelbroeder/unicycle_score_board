from pathlib import Path

import pandas as pd

from src.unicycle.dashboard.scoring import recalculate_all_results
from src.unicycle.db_handler.db_handler import DbHandler
from src.unicycle.db_handler.points_db_handler import PROJECT_ROOT


def get_test_results(
    category: str, age_group: str, id_routines: list[int]
) -> pd.DataFrame:
    db_handler_points = DbHandler(Path(PROJECT_ROOT, "test/points_test.db"), "points")
    df_points = db_handler_points.get_data()
    df_points = df_points.set_index("id_routine").loc[id_routines, :]

    df_points["age_group"] = [age_group] * len(df_points)
    df_points["category"] = [category] * len(df_points)
    print("df_points.reset_index()", df_points.reset_index())
    results = recalculate_all_results(df_points.reset_index())
    print(results)
    results = results.set_index("id_routine")
    return results


def test_individual_female():
    id_routines = [8, 9, 10]
    age_group = "U15"
    category = "individual female"
    results = get_test_results(category, age_group, id_routines)

    assert 0.31 == results.loc[8, "T"]
    assert 0.24 == results.loc[9, "T"]
    assert 0.45 == results.loc[10, "T"]

    assert 0.34 == results.loc[8, "P"]
    assert 0.32 == results.loc[9, "P"]
    assert 0.34 == results.loc[10, "P"]

    assert 0.33 == results.loc[8, "D"]
    assert 0.35 == results.loc[9, "D"]
    assert 0.32 == results.loc[10, "D"]

    assert 32.83 == results.loc[8, "Ergebnis"]
    assert 28.42 == results.loc[9, "Ergebnis"]
    assert 38.75 == results.loc[10, "Ergebnis"]


def test_pair():
    id_routines = [19, 39, 40]
    age_group = "U11"
    category = "pair"
    results = get_test_results(category, age_group, id_routines)

    assert 0.41 == results.loc[19, "T"]
    assert 0.34 == results.loc[39, "T"]
    assert 0.25 == results.loc[40, "T"]

    assert 0.42 == results.loc[19, "P"]
    assert 0.31 == results.loc[39, "P"]
    assert 0.27 == results.loc[40, "P"]

    assert 0.33 == results.loc[19, "D"]
    assert 0.32 == results.loc[39, "D"]
    assert 0.35 == results.loc[40, "D"]

    assert 40.62 == results.loc[19, "Ergebnis"]
    assert 32.42 == results.loc[39, "Ergebnis"]
    assert 26.96 == results.loc[40, "Ergebnis"]


def test_small_group():
    id_routines = [25, 26, 43, 44]
    age_group = "U15"
    category = "small_group"
    results = get_test_results(category, age_group, id_routines)

    assert 0.10 == results.loc[25, "T"]
    assert 0.21 == results.loc[26, "T"]
    assert 0.26 == results.loc[43, "T"]
    assert 0.43 == results.loc[44, "T"]

    assert 0.23 == results.loc[25, "P"]
    assert 0.24 == results.loc[26, "P"]
    assert 0.24 == results.loc[43, "P"]
    assert 0.30 == results.loc[44, "P"]

    assert 0.26 == results.loc[25, "D"]
    assert 0.25 == results.loc[26, "D"]
    assert 0.23 == results.loc[43, "D"]
    assert 0.26 == results.loc[44, "D"]

    assert 17.10 == results.loc[25, "Ergebnis"]
    assert 22.55 == results.loc[26, "Ergebnis"]
    assert 25.20 == results.loc[43, "Ergebnis"]
    assert 35.15 == results.loc[44, "Ergebnis"]


def test_large_group():
    id_routines = [7, 27, 45]
    age_group = "15+"
    category = "large_group"

    results = get_test_results(category, age_group, id_routines)

    assert 0.41 == results.loc[7, "T"]
    assert 0.32 == results.loc[27, "T"]
    assert 0.28 == results.loc[45, "T"]

    assert 0.33 == results.loc[7, "P"]
    assert 0.34 == results.loc[27, "P"]
    assert 0.33 == results.loc[45, "P"]

    assert 0.32 == results.loc[7, "D"]
    assert 0.33 == results.loc[27, "D"]
    assert 0.35 == results.loc[45, "D"]

    assert 36.48 == results.loc[7, "Ergebnis"]
    assert 32.85 == results.loc[27, "Ergebnis"]
    assert 30.68 == results.loc[45, "Ergebnis"]
