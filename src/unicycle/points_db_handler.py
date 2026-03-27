from src.unicycle.constants import *
from src.unicycle.db_handler import DbHandler


PATH_DATABASE = Path("data")
FILE_NAME_DB = Path("points.db")
TABLE_NAME = "points"

class PointsDbHandler(DbHandler):
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
        tp_columns = " REAL,\n".join(TP_SUBCOLS) + " REAL"
        d_columns = " INTEGER,\n".join(D_COLS) + " INTEGER"
        SQL_CREATE_TABLE = f"""
                CREATE TABLE IF NOT EXISTS points (
                id_routine INTEGER PRIMARY KEY,
                {tp_columns},
                {d_columns});
                """
        self.execute(sql_query=SQL_CREATE_TABLE)