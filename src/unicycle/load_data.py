"""data loading class that is used by app.py"""

# %% import packages
import pandas as pd
import sqlite3


# %%
class DataLoader:
    """Handles reading and writing data from SQLite databases."""

    def __init__(self, db_path, table_name):
        self.db_path = db_path
        self.table_name = table_name


    def get_data(self, sql_query = None, par = None)-> pd.DataFrame:
        if sql_query == None:
            sql_query =  f"SELECT * FROM {self.table_name}"
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(sql_query, con = conn, params= par)
            conn.close()
            return df
        except Exception as e:
            print(f"❌ Failed to load data from {self.table_name}: {e}")
            return pd.DataFrame()


    def update_data(self, df: pd.DataFrame):
        try:
            conn = sqlite3.connect(self.db_path)
            df.to_sql(self.table_name, conn, if_exists="replace", index=False)
            conn.close()
            print(f"✅ {self.table_name} aktualisiert.")
        except Exception as e:
            print(f"❌ Fehler beim Schreiben in {self.table_name}: {e}")
