"""Database handler for database riders_routines"""

from pathlib import Path

from src.unicycle.db_handler.db_handler import DbHandler
from src.unicycle.constants import get_path_project_root

PROJECT_ROOT = get_path_project_root()
DIRECTORY_DB = Path("data")
FILE_NAME_DB = Path("riders_routines.db")
TABLE_NAME = "riders_routines"

SQL_CREATE_TABLE = """
       CREATE TABLE IF NOT EXISTS riders_routines (
       id_rider INTEGER,
       id_routine INTEGER,
       PRIMARY KEY (id_rider, id_routine));"""


class RidersRoutinesDbHandler(DbHandler):
    """
    Singleton class for handling riders_routines database operations.
    Ensures only one instance manages database connection and operations.
    Database contains id of the rider and the id of the routines they ride.
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
                Path(PROJECT_ROOT, DIRECTORY_DB, FILE_NAME_DB), TABLE_NAME
            )

    def create_table(self):
        """
        Creates empty database for rider and routine combinations.
        """
        self.execute(sql_query=SQL_CREATE_TABLE)
