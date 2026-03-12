from pathlib import Path
import os

from src.unicycle.db_handler import DbHandler

script_dir = os.path.dirname(os.path.abspath(__file__))
unicycle_score_board_path = Path(script_dir).parent.parent
DIRECTORY_DB = Path("data")
FILE_NAME_DB = Path("routines.db")
TABLE_NAME = "routines"


class RoutinesDbHandler(DbHandler):
    def __init__(self):
        super().__init__(Path(unicycle_score_board_path, DIRECTORY_DB, FILE_NAME_DB), TABLE_NAME)

    def create_table(self):

        SQL_CREATE_TABLE = """CREATE TABLE IF NOT EXISTS routines (
        id_routine INTEGER PRIMARY KEY AUTOINCREMENT,
        routine_name VARCHAR(50),
        category VARCHAR(20),
        age_group VARCHAR(20));"""
        self.execute(sql_query=SQL_CREATE_TABLE)

