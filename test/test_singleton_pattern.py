from src.unicycle.db_handler.riders_db_handler import RidersDbHandler
from src.unicycle.db_handler.riders_routines_db_handler import RidersRoutinesDbHandler
from src.unicycle.db_handler.routines_db_handler import RoutinesDbHandler


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
