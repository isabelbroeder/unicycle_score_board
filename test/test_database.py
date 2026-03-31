from src.unicycle.db_handler.riders_db_handler import RidersDbHandler
from src.unicycle.db_handler.riders_routines_db_handler import RidersRoutinesDbHandler
from src.unicycle.db_handler.routines_db_handler import RoutinesDbHandler


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
