"""Database handler for database routines"""

from pathlib import Path

from src.unicycle.db_handler.db_handler import DbHandler
from src.unicycle.constants import get_path_project_root

PROJECT_ROOT = get_path_project_root()
DIRECTORY_DB = Path("data")
FILE_NAME_DB = Path("routines.db")
TABLE_NAME = "routines"

SQL_CREATE_TABLE = """CREATE TABLE IF NOT EXISTS routines (
id_routine INTEGER PRIMARY KEY AUTOINCREMENT,
routine_name VARCHAR(50),
category VARCHAR(20),
age_group VARCHAR(20));"""


class RoutinesDbHandler(DbHandler):
    """
    Singleton class for handling routine database operations.
    Ensures only one instance manages database connection and operations.
    Database contains id of routine, name of the routine, category and age group.
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
            super().__init__(Path(PROJECT_ROOT, DIRECTORY_DB, FILE_NAME_DB), TABLE_NAME)

    def create_table(self):
        """
        Creates empty database for routine data.
        """
        self.execute(sql_query=SQL_CREATE_TABLE)
