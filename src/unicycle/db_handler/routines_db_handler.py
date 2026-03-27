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
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialised"):
            self.initialised = True
            super().__init__(
                Path(PROJECT_ROOT, DIRECTORY_DB, FILE_NAME_DB), TABLE_NAME
            )

    def create_table(self):
        self.execute(sql_query=SQL_CREATE_TABLE)