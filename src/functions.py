""" calculates ages for different routine groups """


import datetime


def alter_berechnen(geburtsdatum: datetime, datum: datetime) -> int:
    alter = datum.year - geburtsdatum.year
    if geburtsdatum.month > datum.month or (
        geburtsdatum.month == datum.month and geburtsdatum.day > datum.day
    ):  # hatte in dem Jahr noch nicht Geburtstag
        return alter - 1
    return alter


def main():
    print(
        alter_berechnen(datetime.datetime(2002, 12, 4), datetime.datetime(2025, 3, 23))
    )


if __name__ == "__main__":
    main()
