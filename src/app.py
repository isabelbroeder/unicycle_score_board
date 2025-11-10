"""creates dashboard from data in database"""


# %% import packages
from dash import Dash, dash_table, html, Input, Output
import dash_daq as daq
import sqlite3
import pandas as pd

DB_PATH = "../data/fahrerinnen.db"
TABLE_NAME = "fahrerinnen"


# %% DataLoader
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
    """Displays database data in a Dash DataTable with Light/Dark mode toggle."""

    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader
        self.df = self.data_loader.get_data()

        self.app = Dash(__name__, title="Fahrerinnen Dashboard")

        # Build layout
        self.app.layout = self._build_layout()

        # Define callbacks
        self._register_callbacks()

    # --- Themes ---
    LIGHT_THEME = {
        "backgroundColor": "#ffffff",
        "textColor": "#000000",
        "headerBg": "#f0f0f0",
        "headerColor": "#000000",
        "cellBg": "#ffffff",
        "oddRowBg": "#f9f9f9",
        "border": "#dddddd",
    }

    DARK_THEME = {
        "backgroundColor": "#1e1e1e",
        "textColor": "#ffffff",
        "headerBg": "#333333",
        "headerColor": "#ffffff",
        "cellBg": "#222222",
        "oddRowBg": "#2a2a2a",
        "border": "#444444",
    }

    # --- Layout components ---
    def _header(self):
        return html.H1(
            "🏁 Fahrerinnen Übersicht",
            style={"textAlign": "center", "marginBottom": "30px"}
        )

    def _datatable(self, theme):
        if self.df.empty:
            return html.Div("❌ No data loaded from the database.",
                            style={"color": "#ff6b6b", "textAlign": "center", "marginTop": "50px"})
        return dash_table.DataTable(
            id="data-table",
            data=self.df.to_dict("records"),
            columns=[{"name": col, "id": col} for col in self.df.columns],
            page_size=10,
            sort_action="native",
            filter_action="native",
            style_table={"overflowX": "auto"},
            style_header={
                "backgroundColor": theme["headerBg"],
                "color": theme["headerColor"],
                "fontWeight": "bold",
                "textAlign": "center",
                "border": f"1px solid {theme['border']}"
            },
            style_cell={
                "backgroundColor": theme["cellBg"],
                "color": theme["textColor"],
                "textAlign": "left",
                "padding": "8px",
                "whiteSpace": "normal",
                "height": "auto",
                "border": f"1px solid {theme['border']}"
            },
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": theme["oddRowBg"]}
            ],
        )

    def _build_layout(self):
        """Construct the overall layout using sub-components."""
        return html.Div(
            id="page-container",
            style={
                "minHeight": "100vh",
                "padding": "30px",
                "fontFamily": "Arial, sans-serif",
                "position": "relative"
            },
            children=[
                # Toggle button with icons
                html.Div(
                    [
                        html.Span("🌞", id="theme-icon", style={"fontSize": "22px", "marginRight": "8px"}),
                        daq.ToggleSwitch(
                            id="theme-toggle",
                            value=True,  # Start im Darkmode
                            color="#333333",
                            size=40,
                        ),
                    ],
                    style={
                        "position": "absolute",
                        "top": "20px",
                        "left": "25px",
                        "display": "flex",
                        "alignItems": "center",
                        "gap": "10px",
                        "zIndex": 10
                    }
                ),
                self._header(),
                html.Div(id="table-container")
            ]
        )

    def _register_callbacks(self):
        """Define Dash interactivity."""

        @self.app.callback(
            Output("page-container", "style"),
            Output("table-container", "children"),
            Output("theme-icon", "children"),
            Input("theme-toggle", "value")
        )
        def update_theme(is_dark):
            theme = self.DARK_THEME if is_dark else self.LIGHT_THEME
            icon = "🌙" if is_dark else "🌞"

            page_style = {
                "backgroundColor": theme["backgroundColor"],
                "color": theme["textColor"],
                "minHeight": "100vh",
                "padding": "30px",
                "fontFamily": "Arial, sans-serif",
                "transition": "background-color 0.5s, color 0.5s",
            }

            return page_style, self._datatable(theme), icon

    def run(self):
        """Run the Dash server."""
        self.app.run(debug=True)


if __name__ == "__main__":
    dashboard = Dashboard(DataLoader())
    dashboard.run()