import datetime


def calculate_age(date_of_birth: datetime, date: datetime = None) -> int:
    """
    Calculate the age at a given date or today if not specified.

    :param date_of_birth: The date of birth as a datetime object.
    :param date: The date on which to calculate the age. Defaults to today if not provided.
    :return: The age in years as an integer.
    """

    if date is None:
        date = datetime.today()
    age = date.year - date_of_birth.year
    if date_of_birth.month > date.month or (
        date_of_birth.month == date.month and date_of_birth.day > date.day
    ):  # had not yet had their birthday that year
        return age - 1
    return age
