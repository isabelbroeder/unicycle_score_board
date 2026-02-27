"""creates dashboard from data in database"""

from dash import Dash, dash_table, html, Input, Output, State, dcc
import bcrypt
import dash
import dash_bootstrap_components as dbc
import dash_daq as daq
import json
import numpy as np
import os
import pandas as pd
from pathlib import Path
from load_data import DataLoader

BASE_COLS_PARTICIPANT = ["routine_name", "names", "age_group", "category"]
BASE_COLS_JURY = ["routine_name", "age_group", "category"]

T_SUBS = ["Q", "M", "D"]
P_SUBS = ["P", "C", "I"]
D_SUBS = ["S", "B", "N"]

T_COLS = [f"T{i}_{s}" for i in range(1, 5) for s in T_SUBS]
P_COLS = [f"P{i}_{s}" for i in range(1, 5) for s in P_SUBS]
D_COLS = [f"D{i}_{s}" for i in range(1, 5) for s in D_SUBS]

TP_SUBCOLS = T_COLS + P_COLS
SCORE_COLS = TP_SUBCOLS + D_COLS

COLUMN_LABELS = {
    "routine_name": "Kür-Name",
    "names": "Namen*",
    "age_group": "Altersklasse",
    "category_label": "Kategorie",
    "Gesamtpunkte": "Gesamtpunkte",
}

CATEGORY_LABELS = {
    "individual male": "Einzel männlich",
    "individual female": "Einzel weiblich",
    "pair": "Paar",
    "small_group": "Kleingruppe",
    "large_group": "Großgruppe",
}

CATEGORY_ORDER = [
    "Einzel weiblich",
    "Einzel männlich",
    "Paar",
    "Kleingruppe",
    "Großgruppe",
]

JUDGE_LEGEND = {

    "T": {
        "Q": "Anzahl der Einrad-Elemente und Übergänge",
        "M": "Beherrschung und Qualität der Ausführung",
        "D": "Schwierigkeit und Dauer",
    },

    "P": {
        "P": "Präsenz/Ausführung",
        "C": "Komposition/Choreografie",
        "I": "Interpretation der Musik/Timing",
    },

    "D": {
        "S": "Kleine Abstiege",
        "B": "Große Abstiege",
        "N": "Anzahl der Fahrer:innen",
    },
}

script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config.json")
unicycle_score_board_path = Path(script_dir).parent.parent
with open(config_path, "r") as f:
    CONFIG = json.load(f)

STORED_HASH: object = CONFIG["jury_password_hash"].encode()


class Dashboard:
    """Main application class for the unicycle scoring dashboard.

    This class combines the Dash app instance, layout creation,
    callbacks, theming, and execution logic. It provides both participant
    and jury views with optional editing and password-protected access.
    """
    def __init__(self):
        """Initialize the Dash app, themes, layout, and callbacks."""
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
        """Construct and return the root Dash layout container.

        :return: Root page container containing theme toggle, view switch,
        password modal, title, and table placeholder.
        """
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
                        dbc.ModalHeader("🔒 Jury-Zugang",
                                        id="password-modal-header"
                                        ),
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
                                    style={
                                        "width": "100%",
                                        "padding": "8px",
                                        "color": "black",
                                        "backgroundColor": "white",
                                    },
                                ),
                                html.Div(
                                    id="password-error",
                                    style={"color": "red", "marginTop": "10px"},
                                ),
                            ],
                            id="password-modal-body"
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
                            ],
                            id="password-modal-footer"
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

    def _judge_column(self, col, jury_mode):
        """Generate a column definition for judge score columns."""
        judge, sub = col.split("_", 1)

        return {
            "name": [judge, sub],
            "id": col,
            "type": "numeric",
            "editable": jury_mode,
        }

    def _judge_legend_collapsible(self, theme):

        button_style = {
            "backgroundColor": theme["headerBg"],
            "color": theme["textColor"],
            "border": f"1px solid {theme['border']}",
            "borderRadius": "8px",
            "padding": "10px 15px",
            "cursor": "pointer",
            "marginBottom": "10px",
            "fontWeight": "bold",
        }

        container_style = {
            "backgroundColor": theme["cellBg"],
            "border": f"1px solid {theme['border']}",
            "borderRadius": "8px",
            "padding": "15px",
            "marginBottom": "20px",
        }

        grid_style = {
            "display": "grid",
            "gridTemplateColumns": "repeat(3, 1fr)",
            "gap": "20px",
        }

        def build_column(judge, subs):
            header = html.Div(
                f"Judge {judge}",
                style={
                    "fontWeight": "bold",
                    "marginBottom": "8px",
                    "fontSize": "16px",
                },
            )

            items = []

            for sub, text in subs.items():
                label = f"{judge}1–{judge}4 {sub}"

                items.append(
                    html.Div(
                        [
                            html.Span(
                                label,
                                style={"fontWeight": "bold"},
                            ),
                            html.Div(
                                text,
                                style={"fontSize": "13px", "opacity": "0.8"},
                            ),
                        ],
                        style={"marginBottom": "8px"},
                    )
                )

            return html.Div([header] + items)

        legend_content = html.Div(
            [
                build_column("T", JUDGE_LEGEND["T"]),
                build_column("P", JUDGE_LEGEND["P"]),
                build_column("D", JUDGE_LEGEND["D"]),
            ],
            style=grid_style,
        )

        return html.Div(
            [
                html.Button(
                    "📖 Bewertungskriterien anzeigen",
                    id="legend-toggle-btn",
                    n_clicks=0,
                    style=button_style,
                ),

                html.Div(
                    legend_content,
                    id="legend-container",
                    style={
                        **container_style,
                        "display": "none",
                    },
                ),
            ]
        )

    def _datatable(self, df: pd.DataFrame, theme, editable=False, jury_mode=False):
        """Create a Dash DataTable configured for participant or jury mode.

        :param pd.DataFrame df: Source dataframe to display.
        :param dict theme: Theme color dictionary (light or dark).
        :param bool editable: Whether table cells are editable.
        :param bool jury_mode: Whether jury mode is active.
        :return dash_table.DataTable | html.Div: Configured DataTable or
            message if no data available.
        """
        if df.empty:
            return html.Div(
                "❌ Keine Daten geladen.",
                style={"color": "#ff6b6b", "textAlign": "center", "marginTop": "50px"},
            )

        dropdown = {}

        base_cols = BASE_COLS_JURY if jury_mode else BASE_COLS_PARTICIPANT
        ordered_cols = base_cols + T_COLS + P_COLS + D_COLS + ["Gesamtpunkte"]

        if jury_mode:
            df_routines = DataLoader(
                Path(unicycle_score_board_path, "data/routines.db"), "routines"
            ).get_data()
            df_points = DataLoader(
                Path(unicycle_score_board_path, "data/points.db"), "points"
            ).get_data()

            if df_points.empty:
                df_points = pd.DataFrame(columns=BASE_COLS_JURY)

            df = df_routines.merge(df_points, on=BASE_COLS_JURY, how="left")

            for col in ordered_cols:
                if col not in df.columns:
                    df[col] = np.nan

            def set_uneditable_judges(row):
                """Disable D3 and D4 scoring for non-group categories.

                :param pd.Series row: Routine dataframe row.
                :return pd.Series: Modified row with D3/D4 replaced by '–'.
                """
                cat = row["category"]
                if cat in ["individual female", "individual male", "pair"]:
                    for sub in D_SUBS:
                        row[f"D3_{sub}"] = "–"
                        row[f"D4_{sub}"] = "–"
                return row

            df = df.apply(set_uneditable_judges, axis=1)

            # calculation of all points per row ("–" = 0)
            def compute_total(row):
                """Compute total score across all judge columns.

                :param pd.Series row: Scoring dataframe row.
                :return float: Sum of all valid numeric score values.
                """
                total = 0

                for col in TP_SUBCOLS:
                    val = row.get(col)
                    if val == "–" or pd.isna(val):
                        continue
                    try:
                        total += float(val)
                    except Exception:
                        pass

                for col in D_COLS:
                    if col not in row:
                        continue
                    val = row[col]
                    if val == "–" or pd.isna(val):
                        continue
                    try:
                        total += float(val)
                    except Exception:
                        pass

                return total

            df["Gesamtpunkte"] = df.apply(compute_total, axis=1)

        if "category" in df.columns:
            df["category_label"] = (
                df["category"].map(CATEGORY_LABELS).fillna(df["category"])
            )

        df["category_label"] = pd.Categorical(
            df["category_label"],
            categories=CATEGORY_ORDER,
            ordered=True,
        )

        df = df.sort_values(["category_label", "age_group"])

        columns = []

        for col in ordered_cols:

            if col not in df.columns:
                continue

            if col in SCORE_COLS:
                columns.append(self._judge_column(col, jury_mode))

            elif col == "Gesamtpunkte":
                columns.append({
                    "name": ["", COLUMN_LABELS.get(col, col)],
                    "id": col,
                    "type": "numeric",
                    "editable": False,
                })

            else:
                display_col = col

                if col == "category":
                    display_col = "category_label"

                label = COLUMN_LABELS.get(display_col, display_col)

                columns.append({
                    "name": label if not jury_mode else ["", label],
                    "id": display_col,
                    "editable": False,
                })

        table = dash_table.DataTable(
            id="data-table",
            data=df.to_dict("records"),
            columns=columns,
            merge_duplicate_headers=jury_mode,
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
            style_cell_conditional=[
                {
                    "if": {"column_id": "age_group"},
                    "textAlign": "center",
                },
                {
                    "if": {"column_id": "category_label"},
                    "textAlign": "center",
                },
                {
                    "if": {"column_type": "numeric"},
                    "textAlign": "center",
                },
                {
                    "if": {"column_id": "Gesamtpunkte"},
                    "textAlign": "right",
                    "fontWeight": "bold",
                },
            ],
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": theme["oddRowBg"]},
                # lock D3 + D4 for individual + PK (visual + pointer events)
                {
                    "if": {
                        "filter_query": (
                            "{category} = 'individual female' || "
                            "{category} = 'individual male' || "
                            "{category} = 'pair'"
                        ),
                        "column_id": [c for c in D_COLS if c.startswith(("D3_", "D4_"))],
                    },
                    "pointerEvents": "none",
                    "backgroundColor": "#444",
                    "color": "#888",
                },
            ],
        )

        if not jury_mode:
            return html.Div([
                table,
                html.Div(
                    "* Bei Klein- und Großgruppen wird statt der Namen die Anzahl der Teilnehmer angezeigt.",
                    style={
                        "marginTop": "10px",
                        "fontSize": "12px",
                        "opacity": "0.8"
                    }
                )
            ])

        return table

    # ----------------- Callbacks -----------------
    def _register_callbacks(self):
        """Register all Dash callbacks for UI interactivity and persistence."""
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
            """Handle opening, closing, and validating the jury password modal.

            :param int open_clicks: Click count of the view switch button.
            :param int submit_clicks: Click count of the submit password button.
            :param int enter_submit: Submit events from password input.
            :param int cancel_clicks: Click count of cancel button.
            :param bool is_open: Current modal open state.
            :param str password: Entered password value.
            :param bool has_access: Whether jury access is already granted.
            :return tuple[bool, str, str, bool]: Updated modal state, error message,
                cleared input, and access flag.
            """
            ctx = dash.callback_context
            if not ctx.triggered:
                raise dash.exceptions.PreventUpdate
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]

            correct_password_hash = STORED_HASH

            if button_id == "view-switch-btn":
                if has_access:
                    # if jury mode active -> switch back
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
            Output("legend-container", "style"),
            Output("legend-toggle-btn", "children"),
            Input("legend-toggle-btn", "n_clicks"),
            State("legend-container", "style"),
            prevent_initial_call=True,
        )
        def toggle_legend(n_clicks, current_style):

            visible = current_style.get("display") == "block"

            new_display = "none" if visible else "block"

            button_text = (
                "📖 Jury-Kategorien anzeigen"
                if visible
                else "📖 Jury-Kategorien ausblenden"
            )

            current_style["display"] = new_display

            return current_style, button_text

        @self.app.callback(
            Output("page-container", "style"),
            Output("table-container", "children"),
            Output("page-title", "children"),
            Output("view-switch-btn", "children"),
            Output("view-switch-btn", "style"),
            Output("theme-icon", "children"),
            Output("password-modal-header", "style"),
            Output("password-modal-body", "style"),
            Output("password-modal-footer", "style"),
            Output("password-input", "style"),
            Input("theme-toggle", "value"),
            Input("jury-access", "data"),
            prevent_initial_call=False,
        )
        def update_dashboard(is_dark, jury_access):
            """Update theme, view mode, titles, and table content.

            :param bool is_dark: Whether dark theme is enabled.
            :param bool jury_access: Whether jury mode is active.
            :return tuple[dict, object, str, str, str]: Updated page style,
                table component, title text, switch button text, and theme icon.
            """
            theme = self.DARK_THEME if is_dark else self.LIGHT_THEME
            password_input_style = {
                "width": "100%",
                "padding": "8px",
                "color": theme["textColor"],
                "backgroundColor": theme["cellBg"],
                "border": f"1px solid {theme['border']}",
            }
            view_switch_style = {
                "position": "absolute",
                "top": "20px",
                "right": "25px",
                "backgroundColor": theme["headerBg"],
                "color": theme["textColor"],
                "border": f"1px solid {theme['border']}",
                "borderRadius": "8px",
                "padding": "10px 15px",
                "cursor": "pointer",
                "fontSize": "14px",
            }
            modal_content_style = {
                "backgroundColor": theme["cellBg"],
                "color": theme["textColor"],
                "border": f"1px solid {theme['border']}",
            }
            modal_header_style = {
                "backgroundColor": theme["headerBg"],
                "color": theme["textColor"],
                "borderBottom": f"1px solid {theme['border']}",
            }
            modal_body_style = {
                "backgroundColor": theme["cellBg"],
                "color": theme["textColor"],
            }
            modal_footer_style = {
                "backgroundColor": theme["cellBg"],
                "borderTop": f"1px solid {theme['border']}",
            }
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
                df_routines = DataLoader(
                    Path(unicycle_score_board_path, "data/routines.db"), "routines"
                ).get_data()
                title = "⚖️ Jury Übersicht"
                button_text = "👥 Wechsel zu Teilnehmer Ansicht"
                legend = self._judge_legend_collapsible(theme)

                table = html.Div([
                    legend,
                    self._datatable(
                        df_routines, theme, editable=True, jury_mode=True
                    )
                ])
            else:
                df_riders = DataLoader(
                    Path(unicycle_score_board_path, "data/riders.db"), "riders"
                ).get_data(sql_query="SELECT id_rider,name,club FROM riders")
                df_routines = DataLoader(
                    Path(unicycle_score_board_path, "data/routines.db"), "routines"
                ).get_data(
                    sql_query="SELECT id_routine,routine_name,category,age_group FROM routines"
                )
                df_riders2routines = DataLoader(
                    Path(unicycle_score_board_path, "data/riders_routines.db"),
                    "riders_routines",
                ).get_data()
                df_display = df_riders2routines.merge(
                    df_riders, on="id_rider", how="left"
                )
                df_display = df_display.merge(df_routines, on="id_routine", how="left")
                df_display = (
                    (
                        df_display.groupby(["routine_name"], as_index=False).agg(
                            names=("name", lambda x: ", ".join(x))
                        )  # problem bei gleichem Kürnamen
                    )
                    .merge(df_routines, on="routine_name", how="left")
                    .drop(columns="id_routine")
                )
                def format_names(row):
                    """Format the 'names' column for participant display.

                    :param pd.Series row: Row of the participant dataframe.
                    :return str: Display value for the 'names' column.
                    """
                    if row["category"] in ["small_group", "large_group"]:
                        if isinstance(row["names"], str):
                            count = len(row["names"].split(","))
                            return f"{count} Personen"
                    return row["names"]

                df_display["names"] = df_display.apply(format_names, axis=1)
                title = "🏁 Teilnehmer Übersicht"
                button_text = "⚖️ Wechsel zu Jury Ansicht"
                table = self._datatable(
                    df_display, theme, editable=False, jury_mode=False
                )

            return (
                page_style,
                table,
                title,
                button_text,
                view_switch_style,
                icon,
                modal_header_style,
                modal_body_style,
                modal_footer_style,
                password_input_style,
            )

        @self.app.callback(
            Output("data-table", "data", allow_duplicate=True),
            Input("data-table", "data"),
            State("data-table", "data"),
            prevent_initial_call=True,
        )
        def update_points(rows, current_state):
            """Validate edited scores, recompute totals, and persist to database.

            :param list[dict] rows: Updated table rows from DataTable.
            :param list[dict] current_state: Previous table state (unused).
            :return list[dict]: Updated table data with clamped values and totals.
            """
            if not rows:
                raise dash.exceptions.PreventUpdate

            df = pd.DataFrame(rows)

            for col in SCORE_COLS:
                if col not in df.columns:
                    df[col] = np.nan

            # clamp judge values between 0 and 10 (D3 and D4 between 0 and 999)
            def clamp_cell(value, category, colname):

                LOCKED = {"individual female", "individual male", "pair"}

                if colname.startswith(("D3_", "D4_")) and category in LOCKED:
                    return "–"

                if value == "–":
                    return "–"

                try:
                    v = float(value)
                except:
                    return np.nan

                if v < 0:
                    return np.nan

                if colname in D_COLS:
                    if v > 999 or not v.is_integer():
                        return np.nan
                    return int(v)

                if v > 10:
                    return np.nan

                return v

            # Apply clamping per-row and per-scoring column
            if "category" not in df.columns:
                df["category"] = None

            for col in SCORE_COLS:
                df[col] = df.apply(
                    lambda r: clamp_cell(r.get(col), r.get("category"), col), axis=1
                )

            # recompute total
            def compute_total(row):
                total = 0
                for col in SCORE_COLS:
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

            # save to points.db
            try:
                DataLoader(
                    Path(unicycle_score_board_path, "data/points.db"), "points"
                ).update_data(df)
            except Exception as e:
                print("Error saving points:", e)

            return df.to_dict("records")

    def run(self):
        self.app.run(debug=True)


if __name__ == "__main__":
    Dashboard().run()
