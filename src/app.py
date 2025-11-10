"""creates dashboard from data in database"""


# %% import packages
from dash import Dash
import sqlite3
import pandas as pd

DB_PATH = "../data/fahrerinnen.db"
TABLE_NAME = "fahrerinnen"


# %%
class DataLoader:
    """Handles reading data from a SQLite database."""
    def __init__(self, db_path=DB_PATH, table_name=TABLE_NAME):
        self.db_path = db_path
        self.table_name = table_name
        self.df = self._load_data()

    def _load_data(self) -> pd.DataFrame:
        """Load data from the SQLite database."""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(f"SELECT * FROM {self.table_name}", conn)
            conn.close()
            print(f"✅ Loaded {len(df)} rows from '{self.table_name}' in {self.db_path}")
            return df
        except Exception as e:
            print(f"❌ Failed to load data: {e}")
            return pd.DataFrame()

    def get_data(self) -> pd.DataFrame:
        """Return the loaded DataFrame."""
        return self.df




if __name__ == "__main__":
    data_loader = DataLoader()
    print(data_loader.get_data())