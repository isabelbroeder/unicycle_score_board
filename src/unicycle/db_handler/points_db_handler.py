"""Database handler for database points"""

from pathlib import Path

from src.unicycle.constants import TP_SUBCOLS, D_COLS
from src.unicycle.db_handler.db_handler import DbHandler
from src.unicycle.constants import get_path_project_root

PROJECT_ROOT = get_path_project_root()
PATH_DATABASE = Path("data")
FILE_NAME_DB = Path("points.db")
TABLE_NAME = "points"


class PointsDbHandler(DbHandler):
    """
    Singleton class for handling points database operations.
    Ensures only one instance manages database connection and operations.
    Database contains points of the routine given by the judges.
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
        Creates empty database.
        """
        tp_columns = " REAL,\n".join(TP_SUBCOLS) + " REAL"
        d_columns = " INTEGER,\n".join(D_COLS) + " INTEGER"
        sql_create_table = f"""
                CREATE TABLE IF NOT EXISTS points (
                id_routine INTEGER PRIMARY KEY,
                {tp_columns},
                {d_columns});
                """
        self.execute(sql_query=sql_create_table)
