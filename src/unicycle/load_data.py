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

    def get_data(self, sql_query: str = None) -> pd.DataFrame:
        """Load data from the configured SQLite table.

        :param str sql_query: Optional SQL query. If omitted, all rows from the
            configured table are loaded.
        :return pd.DataFrame: Loaded table data or an empty dataframe if the
            table does not exist yet.
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)

            if sql_query is None:
                sql_query = f"SELECT * FROM {self.table_name}"

            df = pd.read_sql_query(sql_query, conn)
            return df

        except Exception as e:
            if "no such table" in str(e).lower():
                return pd.DataFrame()

            print(f"❌ Failed to load data from {self.table_name}: {e}")
            return pd.DataFrame()

        finally:
            if conn is not None:
                conn.close()

    def update_data(self, df: pd.DataFrame, columns: list[str] = None):
        """Write dataframe contents to the configured SQLite table.

        :param pd.DataFrame df: Data to write into the table.
        :param list[str] columns: Optional list of allowed columns to persist.
            If provided, only these columns are written.
        :return None: Writes the dataframe to the database table.
        """
        try:
            if columns is not None:
                df = df[[col for col in columns if col in df.columns]].copy()

            conn = sqlite3.connect(self.db_path)
            df.to_sql(self.table_name, conn, if_exists="replace", index=False)
            conn.close()
            print(f"✅ {self.table_name} updated successfully.")

        except Exception as e:
            print(f"❌ Error writing to {self.table_name}: {e}")

    def update_multiple_rows(
        self, df: pd.DataFrame, key_columns: list, update_columns: list
    ):
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
