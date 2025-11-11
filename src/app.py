"""creates dashboard from data in database"""


# %% import packages
from dash import Dash, dash_table, html, Input, Output
import dash_daq as daq
import sqlite3
import pandas as pd


class DataLoader:
    """Handles reading data from SQLite databases dynamically."""
    def __init__(self, db_path, table_name):
        self.db_path = db_path
        self.table_name = table_name

    def get_data(self) -> pd.DataFrame:
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(f"SELECT * FROM {self.table_name}", conn)
            conn.close()
            return df
        except Exception as e:
            print(f"❌ Failed to load data from {self.table_name}: {e}")
            return pd.DataFrame()


class Dashboard:
    """Displays database data with toggles for Light/Dark and Jury/Teilnehmer view."""

    def __init__(self):
        self.app = Dash(__name__, title="Fahrerinnen & Jury Dashboard")

        # --- Fix white border + hide DAQ dots ---
        self.app.index_string = """
        <!DOCTYPE html>
        <html>
            <head>
                {%metas%}
                <title>{%title%}</title>
                {%favicon%}
                {%css%}
                <style>
                    body { margin: 0; background-color: #000; }
                    .dash-daq-toggle__detail { display: none !important; }
                </style>
            </head>
            <body>
                {%app_entry%}
                <footer>
                    {%config%}
                    {%scripts%}
                    {%renderer%}
                </footer>
            </body>
        </html>
        """

        # --- Themes ---
        self.LIGHT_THEME = {
            "backgroundColor": "#ffffff",
            "textColor": "#000000",
            "headerBg": "#f0f0f0",
            "headerColor": "#000000",
            "cellBg": "#ffffff",
            "oddRowBg": "#f9f9f9",
            "border": "#dddddd",
        }

        self.DARK_THEME = {
            "backgroundColor": "#1e1e1e",
            "textColor": "#ffffff",
            "headerBg": "#333333",
            "headerColor": "#ffffff",
            "cellBg": "#222222",
            "oddRowBg": "#2a2a2a",
            "border": "#444444",
        }

        self.app.layout = self._build_layout()
        self._register_callbacks()

    # ----------------- UI -----------------
    def _build_layout(self):
        return html.Div(
            id="page-container",
            style={
                "minHeight": "100vh",
                "padding": "30px",
                "fontFamily": "Arial, sans-serif",
                "position": "relative",
            },
            children=[
                # Light/Dark mode toggle (top-left)
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

                # Jury/Teilnehmer switch button (top-right)
                html.Button(
                    "👥 Wechsel zu Jury Ansicht",
                    id="view-switch-btn",
                    n_clicks=0,
                    style={
                        "position": "absolute",
                        "top": "20px",
                        "right": "25px",
                        "backgroundColor": "#444",
                        "color": "white",
                        "border": "none",
                        "borderRadius": "8px",
                        "padding": "10px 15px",
                        "cursor": "pointer",
                        "fontSize": "14px",
                    },
                ),

                # Title (dynamisch)
                html.H1(
                    id="page-title",
                    children="🏁 Fahrerinnen Übersicht",
                    style={"textAlign": "center", "marginBottom": "30px"},
                ),

                html.Div(id="table-container"),
            ],
        )

    # ----------------- Data Table -----------------
    def _datatable(self, df: pd.DataFrame, theme):
        if df.empty:
            return html.Div(
                "❌ Keine Daten geladen.",
                style={"color": "#ff6b6b", "textAlign": "center", "marginTop": "50px"},
            )

        return dash_table.DataTable(
            data=df.to_dict("records"),
            columns=[{"name": col, "id": col} for col in df.columns],
            page_size=10,
            sort_action="native",
            filter_action="native",
            style_table={"overflowX": "auto"},
            style_header={
                "backgroundColor": theme["headerBg"],
                "color": theme["headerColor"],
                "fontWeight": "bold",
                "textAlign": "center",
                "border": f"1px solid {theme['border']}",
            },
            style_cell={
                "backgroundColor": theme["cellBg"],
                "color": theme["textColor"],
                "textAlign": "left",
                "padding": "8px",
                "border": f"1px solid {theme['border']}",
            },
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": theme["oddRowBg"]}
            ],
        )

    # ----------------- Callbacks -----------------
    def _register_callbacks(self):
        @self.app.callback(
            Output("page-container", "style"),
            Output("table-container", "children"),
            Output("page-title", "children"),
            Output("view-switch-btn", "children"),
            Output("theme-icon", "children"),
            Input("theme-toggle", "value"),
            Input("view-switch-btn", "n_clicks"),
        )
        def update_dashboard(is_dark, n_clicks):
            theme = self.DARK_THEME if is_dark else self.LIGHT_THEME
            icon = "🌙" if is_dark else "🌞"

            # toggle mode based on button clicks (odd = jury, even = teilnehmer)
            jury_mode = n_clicks % 2 == 1

            if jury_mode:
                df = DataLoader("../data/Jury.db", "jury").get_data()
                title = "⚖️ Jury Übersicht"
                button_text = "👥 Wechsel zu Teilnehmer Ansicht"
            else:
                df = DataLoader("../data/fahrerinnen.db", "fahrerinnen").get_data()
                title = "🏁 Fahrerinnen Übersicht"
                button_text = "⚖️ Wechsel zu Jury Ansicht"

            page_style = {
                "backgroundColor": theme["backgroundColor"],
                "color": theme["textColor"],
                "minHeight": "100vh",
                "padding": "30px",
                "fontFamily": "Arial, sans-serif",
                "transition": "background-color 0.5s, color 0.5s",
            }

            return page_style, self._datatable(df, theme), title, button_text, icon

    def run(self):
        self.app.run(debug=True)


if __name__ == "__main__":
    Dashboard().run()