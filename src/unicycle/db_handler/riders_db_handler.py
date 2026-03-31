from pathlib import Path

from src.unicycle.constants import UNICYCLE_SCORE_BOARD_PATH
from src.unicycle.db_handler.db_handler import DbHandler


PATH_DATABASE = Path("data")
FILE_NAME_DB = Path("riders.db")
TABLE_NAME = "riders"


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
                Path(UNICYCLE_SCORE_BOARD_PATH, PATH_DATABASE, FILE_NAME_DB),
                TABLE_NAME,
            )

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
