"""creates dashboard from data in database"""


# %% import packages
from dash import Dash, dash_table, html, Input, Output, State
import dash_daq as daq
import sqlite3
import pandas as pd

class DataLoader:
    """Handles reading and writing data from SQLite databases."""
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

    def update_data(self, df: pd.DataFrame):
        try:
            conn = sqlite3.connect(self.db_path)
            df.to_sql(self.table_name, conn, if_exists='replace', index=False)
            conn.close()
            print("✅ Jury-Datenbank aktualisiert.")
        except Exception as e:
            print(f"❌ Fehler beim Schreiben der Jury-Datenbank: {e}")

    def get_kategorien_list(self) -> list:
        """Return list of unique Kategorien from Jury database."""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(f"SELECT DISTINCT Kategorie FROM {self.table_name}", conn)
            conn.close()
            return df['Kategorie'].tolist()
        except Exception as e:
            print(f"❌ Fehler beim Abrufen der Kategorien: {e}")
            return []

class Dashboard:
    def __init__(self):
        self.app = Dash(__name__, title="Fahrerinnen & Jury Dashboard", suppress_callback_exceptions=True)

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

        # --- Layout ---
        self.app.layout = self._build_layout()
        self._register_callbacks()

    # ----------------- UI -----------------
    def _build_layout(self):
        df = DataLoader("../data/fahrerinnen.db", "fahrerinnen").get_data()
        theme = self.DARK_THEME

        return html.Div(
            id="page-container",
            style={
                "minHeight": "100vh",
                "padding": "30px",
                "fontFamily": "Arial, sans-serif",
                "position": "relative",
            },
            children=[
                # Light/Dark toggle
                html.Div(
                    [
                        html.Span("🌞", id="theme-icon", style={"fontSize": "22px", "marginRight": "8px"}),
                        daq.ToggleSwitch(id="theme-toggle", value=True, color="#333333", size=40),
                    ],
                    style={
                        "position": "absolute",
                        "top": "20px",
                        "left": "25px",
                        "display": "flex",
                        "alignItems": "center",
                        "gap": "10px",
                    },
                ),
                # View switch button
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
                html.H1(
                    id="page-title",
                    children="🏁 Teilnehmer Übersicht",
                    style={"textAlign": "center", "marginBottom": "30px"},
                ),
                html.Div(id="table-container", children=[]),
            ],
        )

    # ----------------- Data Table -----------------
    def _datatable(self, df: pd.DataFrame, theme, editable=False, jury_mode=False):
        if df.empty:
            return html.Div(
                "❌ Keine Daten geladen.",
                style={"color": "#ff6b6b", "textAlign": "center", "marginTop": "50px"},
            )

        dropdown = {}

        if jury_mode:
            # Kürzel aus Jury-Datenbank abrufen -> jetzt Kategorien
            kategorien_list = DataLoader("../data/Jury.db", "jury").get_kategorien_list()
            # Eine Spalte pro Kategorie für Teilnahme
            for k in kategorien_list:
                if k not in df.columns:
                    df[k] = False
                dropdown[k] = {"options": [{"label": "✅", "value": True}, {"label": "⬜", "value": False}]}

            if "Punkte" not in df.columns:
                df["Punkte"] = ""

        # Spalten definieren
        columns = []
        for col in df.columns:
            if jury_mode and col in kategorien_list:
                columns.append({"name": col, "id": col, "type": "any", "editable": editable})
            elif col == "Punkte":
                columns.append({"name": col, "id": col, "type": "numeric", "editable": editable})
            else:
                columns.append({"name": col, "id": col, "editable": editable})

        return dash_table.DataTable(
            id="data-table",
            data=df.to_dict("records"),
            columns=columns,
            dropdown=dropdown,
            editable=editable,
            filter_action="native",
            sort_action="native",
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
            jury_mode = n_clicks % 2 == 1

            page_style = {
                "backgroundColor": theme["backgroundColor"],
                "color": theme["textColor"],
                "minHeight": "100vh",
                "padding": "30px",
                "fontFamily": "Arial, sans-serif",
                "transition": "background-color 0.5s, color 0.5s",
            }

            if jury_mode:
                df = DataLoader("../data/fahrerinnen.db", "fahrerinnen").get_data()
                title = "⚖️ Jury Übersicht"
                button_text = "👥 Wechsel zu Teilnehmer Ansicht"
                table = self._datatable(df, theme, editable=True, jury_mode=True)
            else:
                df = DataLoader("../data/fahrerinnen.db", "fahrerinnen").get_data()
                title = "🏁 Teilnehmer Übersicht"
                button_text = "⚖️ Wechsel zu Jury Ansicht"
                table = self._datatable(df, theme, editable=False, jury_mode=False)

            return page_style, table, title, button_text, icon

        @self.app.callback(
            Output("data-table", "data", allow_duplicate=True),
            Input("data-table", "active_cell"),
            State("data-table", "data"),
            prevent_initial_call=True,
        )
        def save_jury_changes(active_cell, rows):
            if active_cell and rows:
                loader = DataLoader("../data/Jury.db", "jury")
                loader.update_data(pd.DataFrame(rows))
            return rows

    def run(self):
        self.app.run(debug=True)


if __name__ == "__main__":
    Dashboard().run()
