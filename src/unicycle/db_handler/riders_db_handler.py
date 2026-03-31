"""Database handler for database riders"""

from pathlib import Path

from src.unicycle.constants import get_path_project_root
from src.unicycle.db_handler.db_handler import DbHandler

PROJECT_ROOT = get_path_project_root()
PATH_DATABASE = Path("data")
FILE_NAME_DB = Path("riders.db")
TABLE_NAME = "riders"

SQL_CREATE_TABLE = """
        CREATE TABLE IF NOT EXISTS riders (
        id_rider INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(50),
        gender CHAR(1),
        date_of_birth DATE,
        age_competition_day INTEGER,
        club VARCHAR(50));"""


class RidersDbHandler(DbHandler):
    """
    Singleton class for handling rider database operations.
    Ensures only one instance manages database connection and operations.
    Database contains rider data (id of the rider, name, gender, date of birth, the age at day of the competition and the club)
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Creates a new instance if one does not exist otherwise returning existing one.
        """

        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initializes the database handler with the database path and table name.
        Ensures initialization occurs only once.
        """
        if not hasattr(self, "initialised"):
            self.initialised = True
            super().__init__(
                Path(PROJECT_ROOT, PATH_DATABASE, FILE_NAME_DB),
                TABLE_NAME,
            )

    def create_table(self):
        """
        Creates empty database for rider data.
        """

        self.execute(sql_query=SQL_CREATE_TABLE)
