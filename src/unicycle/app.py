"""creates dashboard from data in database"""

# %% import packages
from dash import Dash, dash_table, html, Input, Output, State, dcc
import dash
import dash_daq as daq
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
import json
import bcrypt

from load_data import DataLoader


ROUTINE_DATA = ["routine_name", "category", "age_group"]


# constants
with open("config.json", "r") as f:
    CONFIG = json.load(f)

STORED_HASH: object = CONFIG["jury_password_hash"].encode()


class Dashboard:
    def __init__(self):
        self.app = Dash(
            __name__,
            title="Fahrerinnen & Jury Dashboard",
            suppress_callback_exceptions=True,
            external_stylesheets=[dbc.themes.DARKLY],
        )

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
                        html.Span(
                            "🌞",
                            id="theme-icon",
                            style={"fontSize": "22px", "marginRight": "8px"},
                        ),
                        daq.ToggleSwitch(
                            id="theme-toggle", value=True, color="#333333", size=40
                        ),
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
                # jury switch button
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
                # password needed to access jury mode
                dcc.Store(id="jury-access", data=False),
                dbc.Modal(
                    [
                        dbc.ModalHeader("🔒 Jury-Zugang"),
                        dbc.ModalBody(
                            [
                                html.Div(
                                    "Bitte Passwort eingeben:",
                                    style={"marginBottom": "10px"},
                                ),
                                dcc.Input(
                                    id="password-input",
                                    type="password",
                                    placeholder="Passwort",
                                    n_submit=0,
                                    style={"width": "100%", "padding": "8px"},
                                ),
                                html.Div(
                                    id="password-error",
                                    style={"color": "red", "marginTop": "10px"},
                                ),
                            ]
                        ),
                        dbc.ModalFooter(
                            [
                                dbc.Button(
                                    "Abbrechen",
                                    id="cancel-password",
                                    color="secondary",
                                    n_clicks=0,
                                ),
                                dbc.Button(
                                    "Bestätigen",
                                    id="submit-password",
                                    color="primary",
                                    n_clicks=0,
                                ),
                            ]
                        ),
                    ],
                    id="password-modal",
                    is_open=False,
                    backdrop="static",
                ),
                html.H1(
                    id="page-title",
                    children="🏁 Teilnehmer Übersicht",
                    style={"textAlign": "center", "marginBottom": "30px"},
                ),
                html.Div(id="table-container", children=[]),
            ],
        )

    def _datatable(self, df: pd.DataFrame, theme, editable=False, jury_mode=False):
        if df.empty:
            return html.Div(
                "❌ Keine Daten geladen.",
                style={"color": "#ff6b6b", "textAlign": "center", "marginTop": "50px"},
            )

        dropdown = {}

        if jury_mode:
            df_routines = DataLoader("../../data/routines.db", "routines").get_data()
            df_points = DataLoader("../../data/points.db", "points").get_data()

            # Sicherstellen, dass alle Kürkombinationen einmalig sind
            df_routines = df_routines.drop_duplicates(subset=ROUTINE_DATA)
            if df_points.empty:
                df_points = pd.DataFrame(columns=ROUTINE_DATA)
            df_points = df_points.drop_duplicates(subset=ROUTINE_DATA)

            # Merge ohne Duplikate, Kürstruktur bleibt gleich
            key_cols = ROUTINE_DATA
            cols_to_drop = [
                c
                for c in df_points.columns
                if c in df_routines.columns and c not in key_cols
            ]
            df_points = df_points.drop(columns=cols_to_drop)
            df = df_routines.merge(df_points, on=key_cols, how="left")

            all_judges = (
                [f"T{i}" for i in range(1, 5)]
                + [f"P{i}" for i in range(1, 5)]
                + [f"D{i}" for i in range(1, 5)]
            )
            for j in all_judges:
                if j not in df.columns:
                    df[j] = np.nan

            def set_uneditable_judges(row):
                cat = row["category"]
                if cat in ["individual", "pair"]:
                    row["D3"] = row["D4"] = "–"
                return row

            df = df.apply(set_uneditable_judges, axis=1)

            # calculation of all points per row ("–" = 0)
            def compute_total(row):
                total = 0
                for col in all_judges:
                    val = row[col]
                    if val == "–" or pd.isna(val):
                        total += 0
                    else:
                        try:
                            total += float(val)
                        except:
                            total += 0
                return total

            df["Gesamtpunkte"] = df.apply(compute_total, axis=1)

        columns = []
        for col in df.columns:
            # Jury scoring columns numeric display (T1–T4, P1–P4)
            if jury_mode and col in [f"T{i}" for i in range(1, 5)] + [
                f"P{i}" for i in range(1, 5)
            ] + [f"D{i}" for i in range(1, 3)]:
                columns.append(
                    {"name": col, "id": col, "type": "numeric", "editable": True}
                )

            # D3 + D4 (special locking logic handled row-wise via style + callback)
            elif jury_mode and col in ["D3", "D4"]:
                columns.append(
                    {"name": col, "id": col, "type": "numeric", "editable": True}
                )

            elif col == "Gesamtpunkte":
                columns.append(
                    {"name": col, "id": col, "type": "numeric", "editable": False}
                )
            else:
                columns.append({"name": col, "id": col, "editable": False})

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
                {"if": {"row_index": "odd"}, "backgroundColor": theme["oddRowBg"]},
                # lock D3 + D4 for individual + PK (visual + pointer events)
                {
                    "if": {
                        "filter_query": "{category} = 'individual'",
                        "column_id": ["D3", "D4"],
                    },
                    "pointerEvents": "none",
                    "color": "#888",
                },
                {
                    "if": {
                        "filter_query": "{category} = 'pair'",
                        "column_id": ["D3", "D4"],
                    },
                    "pointerEvents": "none",
                    "color": "#888",
                },
            ],
        )

    # ----------------- Callbacks -----------------
    def _register_callbacks(self):
        # --- Password modal open/close ---
        @self.app.callback(
            Output("password-modal", "is_open"),
            Output("password-error", "children"),
            Output("password-input", "value"),
            Output("jury-access", "data"),
            Input("view-switch-btn", "n_clicks"),
            Input("submit-password", "n_clicks"),
            Input("cancel-password", "n_clicks"),
            Input("password-input", "n_submit"),
            State("password-modal", "is_open"),
            State("password-input", "value"),
            State("jury-access", "data"),
            prevent_initial_call=True,
        )
        def toggle_password_modal(
            open_clicks,
            submit_clicks,
            enter_submit,
            cancel_clicks,
            is_open,
            password,
            has_access,
        ):
            ctx = dash.callback_context
            if not ctx.triggered:
                raise dash.exceptions.PreventUpdate
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]

            correct_password_hash = STORED_HASH

            if button_id == "view-switch-btn":
                if has_access:
                    # if jury mode activ -> switch back
                    return False, "", "", False
                else:
                    # if jury mode is about to be activated -> ask for password
                    return True, "", "", False

            elif button_id in ("submit-password", "password-input"):
                if password and bcrypt.checkpw(
                    password.encode(), correct_password_hash
                ):
                    return False, "", "", True  # correct
                else:
                    return True, "❌ Falsches Passwort!", "", False

            elif button_id == "cancel-password":
                return False, "", "", has_access
            else:
                raise dash.exceptions.PreventUpdate

        @self.app.callback(
            Output("page-container", "style"),
            Output("table-container", "children"),
            Output("page-title", "children"),
            Output("view-switch-btn", "children"),
            Output("theme-icon", "children"),
            Input("theme-toggle", "value"),
            Input("jury-access", "data"),
            prevent_initial_call=False,
        )
        def update_dashboard(is_dark, jury_access):
            theme = self.DARK_THEME if is_dark else self.LIGHT_THEME
            icon = "🌙" if is_dark else "🌞"
            jury_mode = jury_access

            page_style = {
                "backgroundColor": theme["backgroundColor"],
                "color": theme["textColor"],
                "minHeight": "100vh",
                "padding": "30px",
                "fontFamily": "Arial, sans-serif",
                "transition": "background-color 0.5s, color 0.5s",
            }

            if jury_mode:
                df_routines = DataLoader("../../data/routines.db", "routines").get_data()
                title = "⚖️ Jury Übersicht"
                button_text = "👥 Wechsel zu Teilnehmer Ansicht"
                table = self._datatable(
                    df_routines, theme, editable=True, jury_mode=True
                )
            else:
                df_riders = DataLoader("../../data/riders.db", "riders").get_data()
                title = "🏁 Teilnehmer Übersicht"
                button_text = "⚖️ Wechsel zu Jury Ansicht"
                table = self._datatable(
                    df_riders, theme, editable=False, jury_mode=False
                )

            return page_style, table, title, button_text, icon

        @self.app.callback(
            Output("data-table", "data", allow_duplicate=True),
            Input("data-table", "data"),
            State("data-table", "data"),
            prevent_initial_call=True,
        )
        def update_points(rows, current_state):
            # rows: new data submitted from the DataTable
            # current_state: previous state (not used, kept for signature compatibility)
            if not rows:
                raise dash.exceptions.PreventUpdate

            df = pd.DataFrame(rows)

            # judge columns (we handle them as text in DB; convert safely here)
            scoring_cols = (
                [f"T{i}" for i in range(1, 5)]
                + [f"P{i}" for i in range(1, 5)]
                + [f"D{i}" for i in range(1, 5)]
            )

            # Ensure columns exist
            for col in scoring_cols:
                if col not in df.columns:
                    df[col] = np.nan

            # --- CLEAN / VALIDATE ---
            def clamp_cell(value, category, colname):
                # If D3 or D4 and category is individual or pair -> force "–" and disallow numeric entry
                if colname in ["D3", "D4"] and category in ["individual", "pair"]:
                    return "–"
                # Accept the dash as-is
                if value == "–":
                    return "–"
                # Try to convert to float; if not possible, treat as 0
                try:
                    v = float(value)
                except Exception:
                    # Some entries might be pandas NaN or None; treat as 0
                    return 0
                # Clamp to 0..10
                if v < 0:
                    return 0
                if v > 10:
                    return 10
                # If it's an integer-like value, keep it as float/int (DB will store as text/numeric on to_sql)
                # Return numeric for downstream total calculation
                return v

            # Apply clamping per-row and per-scoring column
            if "category" not in df.columns:
                df["category"] = None

            for col in scoring_cols:
                df[col] = df.apply(
                    lambda r: clamp_cell(r.get(col), r.get("category"), col), axis=1
                )

            # --- Recompute total ---
            def compute_total(row):
                total = 0
                for col in scoring_cols:
                    val = row.get(col)
                    if val == "–" or pd.isna(val):
                        total += 0
                    else:
                        try:
                            total += float(val)
                        except:
                            total += 0
                return total

            df["Gesamtpunkte"] = df.apply(compute_total, axis=1)

            # --- Save to DB (points.db) ---
            # Ensure the points DB exists or will be created automatically by to_sql
            # We only write the columns present in df (which include kuer keys + judge cols + Gesamtpunkte)
            try:
                DataLoader("../../data/points.db", "points").update_data(df)
            except Exception as e:
                print("Fehler beim Speichern der Punkte:", e)

            return df.to_dict("records")

    def run(self):
        self.app.run(debug=True)


if __name__ == "__main__":
    Dashboard().run()
