from datetime import datetime
from pathlib import Path
import os
import sqlite3

from src.unicycle.db_handler import adapt_date_iso, convert_date
from src.unicycle.db_handler import DbHandler

script_dir = os.path.dirname(os.path.abspath(__file__))
unicycle_score_board_path = Path(script_dir).parent.parent
path_database = Path("data")
file_name_db_riders = Path("riders.db")
table_name_riders = "riders"


class RidersDbHandler(DbHandler):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialised"):
            self.initialised = True
            super().__init__(
                Path(unicycle_score_board_path, path_database, file_name_db_riders),
                table_name_riders,
            )
        #self.connect()

    def create_table(self):
        SQL_CREATE_TABLE = """
                CREATE TABLE IF NOT EXISTS riders (
                id_rider INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(50),
                gender CHAR(1),
                date_of_birth DATE,
                age_competition_day INTEGER,
                club VARCHAR(50));"""

        self.execute(sql_query=SQL_CREATE_TABLE)
