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

    def get_data(self, sql_query: str = None, par = None)-> pd.DataFrame:
        """
        Load data from a SQLite database into a pandas DataFrame.

        Parameters
        ----------
        sql_query : str, optional
        SQL SELECT query to execute.
        If None, defaults to:
        ``SELECT * FROM {self.table_name}``

        par : sequence or mapping, optional
            Parameters to bind to the SQL query.
            - Use a sequence (tuple/list) for ``?`` placeholders
            - Use a mapping (dict) for ``:name`` placeholders

        Returns
        -------
        pd.DataFrame containing the query results.
        Returns an empty DataFrame if the query fails.
        """

        if sql_query == None:
            sql_query = f"SELECT * FROM {self.table_name}"
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(sql_query, con = conn, params = par)
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
            print(f"✅ {self.table_name} updated successfully.")
        except Exception as e:
            print(f"❌ Error writing to {self.table_name}: {e}")


    def update_multiple_rows(self, df: pd.DataFrame, key_columns: list, update_columns: list):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            sql = f"""
            UPDATE {self.table_name}
            SET {', '.join([f"{col} = ?" for col in update_columns])}
            WHERE {" AND ".join([f"{col} = ?" for col in key_columns])}
            """

            data = [
                [row[col] for col in update_columns] + [row[col] for col in key_columns]
                for _, row in df.iterrows()
            ]

            cursor.executemany(sql, data)
            conn.commit()
            conn.close()
            print(f"✅ {update_columns} in {self.table_name} updated successfully.")
        except Exception as e:
            print(f"❌ Error updating {update_columns} in {self.table_name}: {e}")
