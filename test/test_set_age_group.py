from src.unicycle.create_database import set_age_group


def test_set_age_group():
    assert "U13" == set_age_group(12, ["U13", "U15", "15+"])
    assert "U15" == set_age_group(14, ["U13", "U15", "15+"])
    assert "15+" == set_age_group(15, ["U13", "U15", "15+"])
    assert "15+" == set_age_group(16, ["U13", "U15", "15+"])
