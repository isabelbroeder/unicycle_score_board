"""Data loading class that is used by app.py."""

import datetime
import sqlite3
import pandas as pd

from abc import ABC
from pathlib import Path


class DbHandler(ABC):
    """Handles reading and writing data from SQLite databases."""

    def __init__(self, db_path: Path, table_name: str):
        """
        Create database and connect to it.

        db_path -- path to database
        table_name --  name of table
        """

        self.db_path = db_path
        self.table_name = table_name
        try:
            self.db_connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                detect_types=sqlite3.PARSE_DECLTYPES,
            )
            self.cursor = self.db_connection.cursor()
        except Exception as e:
            print(f"❌ Failed to connect database {self.table_name}: {e}")
            self.is_connected = False
        self.is_connected = True
        sqlite3.register_converter("DATE", convert_date)
        sqlite3.register_adapter(datetime.date, adapt_date_iso)

    def create_table(self):
        pass

    def disconnect(self):
        """Disconnect DbHandler from database."""
        if not self.is_connected:
            pass
        self.db_connection.close()
        self.is_connected = False

    def connect(self):
        """Connect DbHandler with database."""
        if self.is_connected:
            pass
        try:
            self.db_connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                detect_types=sqlite3.PARSE_DECLTYPES,
            )
            self.cursor = self.db_connection.cursor()
        except Exception as e:
            print(f"❌ Failed to connect database {self.table_name}: {e}")
            self.is_connected = False
        self.is_connected = True

    def get_data(self, sql_query: str = None, par=None) -> pd.DataFrame:
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

        if sql_query is None:
            sql_query = f"SELECT * FROM {self.table_name}"
        try:
            df = pd.read_sql_query(sql_query, con=self.db_connection, params=par)
            return df
        except Exception as e:
            print(f"❌ Failed to load data from {self.table_name}: {e}")
            return pd.DataFrame()

    def execute(self, sql_query: str, params=None):
        """
        Execute sql query

        sql_query: sql query which will be executed
        params: optional, parameter for sql query
        """
        try:
            if params is None:
                self.cursor.execute(sql_query)
            else:
                for param in params:
                    self.cursor.execute(sql_query, param)
            self.db_connection.commit()
        except Exception as e:
            print(f"❌ Error executing sql query {sql_query} on {self.table_name}: {e}")

    def update_data(self, df: pd.DataFrame, columns: list[str] = None):
        """Write dataframe contents to the configured SQLite table.

        pd.DataFrame df: Data to write into the table.
        list[str] columns: Optional list of allowed columns to persist.
            If provided, only these columns are written.
        """
        try:
            if columns is not None:
                df = df[[col for col in columns if col in df.columns]].copy()

            df.to_sql(
                self.table_name, self.db_connection, if_exists="replace", index=False
            )
            print(f"✅ {self.table_name} updated successfully.")

        except Exception as e:
            print(f"❌ Error writing to {self.table_name}: {e}")

    def update_multiple_rows(
        self, df: pd.DataFrame, key_columns: list, update_columns: list
    ):
        """
        Update data in database
        Keyword arguments:
            df -- Dataframe which will be inserted in database
            key_columns -- Key columns in database
            update_columns -- Columns in database which will be updated
        """

        try:
            sql = f"""
            UPDATE {self.table_name}
            SET {', '.join([f"{col} = ?" for col in update_columns])}
            WHERE {" AND ".join([f"{col} = ?" for col in key_columns])}
            """
            data = [
                [row[col] for col in update_columns] + [row[col] for col in key_columns]
                for _, row in df.iterrows()
            ]
            self.cursor.executemany(sql, data)
            self.db_connection.commit()
            print(f"✅ {update_columns} in {self.table_name} updated successfully.")
        except Exception as e:
            print(f"❌ Error updating {update_columns} in {self.table_name}: {e}")


def adapt_date_iso(val):
    """Adapt datetime.date to ISO 8601 date."""
    return val.isoformat()


def convert_date(val):
    """Convert ISO 8601 date to datetime.date object."""
    return datetime.date.fromisoformat(val.decode())
