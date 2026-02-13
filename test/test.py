import datetime

#from src.unicycle import functions, create_database
#from src.unicycle import set_age_group
from src.unicycle.functions import calculate_age
from src.unicycle.create_database import set_age_group



def test_calculate_age_year():
    assert 23 == calculate_age(datetime.datetime(2002,2, 24), datetime.datetime(2025,4, 20))
    assert 22 == calculate_age(datetime.datetime(2002,8, 24), datetime.datetime(2025,4, 20))

def test_calculate_age_month():
    assert 22 == calculate_age(datetime.datetime(2003,5, 1), datetime.datetime(2025,5, 12))
    assert 21 == calculate_age(datetime.datetime(2003,5, 20), datetime.datetime(2025,5, 12))

def test_calculate_age_day():
    assert 21 == calculate_age(datetime.datetime(2004,6, 27), datetime.datetime(2025,6, 27))


def test_set_age_group():
    assert "U13" == set_age_group(12, ["U13", "U15", "15+"])
    assert "U15" == set_age_group(14,["U13","U15", "15+"])
    assert "15+" == set_age_group(15, ["U13", "U15", "15+"])
    assert "15+" == set_age_group(16, ["U13", "U15", "15+"])






