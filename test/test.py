import datetime

from src.unicycle.create_database import set_age_group, calculate_age
from src.unicycle.db_handler.riders_db_handler import RidersDbHandler
from src.unicycle.db_handler.riders_routines_db_handler import RidersRoutinesDbHandler
from src.unicycle.db_handler.routines_db_handler import RoutinesDbHandler


def test_calculate_age_year():
    assert 23 == calculate_age(
        datetime.datetime(2002, 2, 24), datetime.datetime(2025, 4, 20)
    )
    assert 22 == calculate_age(
        datetime.datetime(2002, 8, 24), datetime.datetime(2025, 4, 20)
    )


def test_calculate_age_month():
    assert 22 == calculate_age(
        datetime.datetime(2003, 5, 1), datetime.datetime(2025, 5, 12)
    )
    assert 21 == calculate_age(
        datetime.datetime(2003, 5, 20), datetime.datetime(2025, 5, 12)
    )


def test_calculate_age_day():
    assert 21 == calculate_age(
        datetime.datetime(2004, 6, 27), datetime.datetime(2025, 6, 27)
    )


def test_set_age_group():
    assert "U13" == set_age_group(12, ["U13", "U15", "15+"])
    assert "U15" == set_age_group(14, ["U13", "U15", "15+"])
    assert "15+" == set_age_group(15, ["U13", "U15", "15+"])
    assert "15+" == set_age_group(16, ["U13", "U15", "15+"])


def test_database():
    routines_db_handler = RoutinesDbHandler()
    routines = routines_db_handler.get_data()

    riders_routines_db_handler = RidersRoutinesDbHandler()
    riders_routines = riders_routines_db_handler.get_data()

    riders_db_handler = RidersDbHandler()
    riders = riders_db_handler.get_data()
    df = riders_routines.merge(riders, on="id_rider", how="left")
    df = df.merge(routines, on="id_routine", how="left")
    assert (
        (df["name"] == "Lara Müller") & (df["routine_name"] == "Heinzelmännchen")
    ).any()
    assert (
        (df["name"] == "Max Mustermann") & (df["routine_name"] == "Max und Moritz")
    ).any()

def test_singleton_pattern_riders():
    riders_db_handler1 = RidersDbHandler()
    riders_db_handler2 = RidersDbHandler()
    assert riders_db_handler1 == riders_db_handler2

def test_singleton_pattern_riders_routines():
    riders_routines_db_handler1 = RidersRoutinesDbHandler()
    riders_routines_db_handler2 = RidersRoutinesDbHandler()
    assert riders_routines_db_handler1 == riders_routines_db_handler2

def test_singleton_pattern_routines():
    routines_db_handler1 = RoutinesDbHandler()
    routines_db_handler2 = RoutinesDbHandler()
    assert routines_db_handler1 == routines_db_handler2

