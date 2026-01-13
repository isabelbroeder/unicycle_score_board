import datetime

from src.unicycle.functions import calculate_age



def test_calculate_age():
    assert 23 == calculate_age(datetime.datetime(2002,2, 24), datetime.datetime(2025,12, 31))

