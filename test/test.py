import datetime

from src.unicycle.functions import calculate_age


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
