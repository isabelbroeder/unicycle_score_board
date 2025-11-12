"""creates dashboard from data in database"""


# %% import packages
from dash import Dash, dash, dash_table, html
import sqlite3
import pandas as pd
from dash.html import Div

DB_PATH = "../data/fahrerinnen.db"
TABLE_NAME = "fahrerinnen"


# %%
class DataLoader:
    """Handles reading data from a SQLite database."""
    def __init__(self, db_path=DB_PATH, table_name=TABLE_NAME) -> None:
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




# %% Dashboard
class Dashboard:
    """Displays database data in a dark mode Dash DataTable."""

    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader
        self.df = self.data_loader.get_data()

        self.app = Dash(__name__, title="Fahrerinnen Dashboard")

        # Build layout
        self.app.layout = self._build_layout()

    # --- Layout components ---
    def _header(self):
        return html.H1(
            "🏁 Fahrerinnen Übersicht",
            style={"textAlign": "center", "marginBottom": "30px"}
        )

    def _datatable(self):
        if self.df.empty:
            return html.Div("❌ No data loaded from the database.",
                            style={"color": "#ff6b6b", "textAlign": "center", "marginTop": "50px"})
        return dash_table.DataTable(
            data=self.df.to_dict("records"),
            columns=[{"name": col, "id": col} for col in self.df.columns],
            page_size=10,
            sort_action="native",
            filter_action="native",
            style_table={"overflowX": "auto"},
            style_header={
                "backgroundColor": "#333333",
                "color": "#ffffff",
                "fontWeight": "bold",
                "textAlign": "center",
                "border": "1px solid #444"
            },
            style_cell={
                "backgroundColor": "#222222",
                "color": "#f0f0f0",
                "textAlign": "left",
                "padding": "8px",
                "whiteSpace": "normal",
                "height": "auto",
                "border": "1px solid #333"
            },
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": "#2a2a2a"}
            ],
        )

    def _build_layout(self):
        """Construct the overall layout using sub-components."""
        return html.Div(
            style={
                "backgroundColor": "#1e1e1e",
                "color": "#ffffff",
                "minHeight": "100vh",
                "padding": "30px",
                "fontFamily": "Arial, sans-serif"
            },
            children=[
                self._header(),
                self._datatable()
            ]
        )

    def run(self):
        """Run the Dash server."""
        self.app.run()

if __name__ == "__main__":
    dashboard = Dashboard(DataLoader())
    dashboard.run()