from pathlib import Path
import os

from src.unicycle.db_handler.db_handler import DbHandler

script_dir = os.path.dirname(os.path.abspath(__file__))
unicycle_score_board_path = Path(script_dir).parent.parent
DIRECTORY_DB = Path("data")
FILE_NAME_DB = Path("riders_routines.db")
TABLE_NAME = "riders_routines"


class RidersRoutinesDbHandler(DbHandler):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialised"):
            self.initialised = True
            super().__init__(
                Path(unicycle_score_board_path, DIRECTORY_DB, FILE_NAME_DB), TABLE_NAME
            )

    def create_table(self):
        SQL_CREATE_TABLE = """
        CREATE TABLE IF NOT EXISTS riders_routines (
        id_rider INTEGER,
        id_routine INTEGER,
        PRIMARY KEY (id_rider, id_routine));"""
        self.execute(sql_query=SQL_CREATE_TABLE)
