"""creates dashboard from data in database"""

from dash import Dash, dash_table, html, Input, Output, State, dcc
import bcrypt
import dash
import dash_bootstrap_components as dbc
import dash_daq as daq
import json
import numpy as np
import pandas as pd
from pathlib import Path
from load_data import DataLoader

BASE_COLS_PARTICIPANT = ["routine_name", "names", "age_group", "category"]
BASE_COLS_JURY = ["id_routine", "routine_name", "age_group", "category"]

T_SUBS = ["Q", "M", "D"]
P_SUBS = ["P", "C", "I"]
D_SUBS = ["S", "B", "N"]

T_COLS = [f"T{i}_{s}" for i in range(1, 5) for s in T_SUBS]
P_COLS = [f"P{i}_{s}" for i in range(1, 5) for s in P_SUBS]
D_COLS = [f"D{i}_{s}" for i in range(1, 5) for s in D_SUBS]

TP_SUBCOLS = T_COLS + P_COLS
SCORE_COLS = TP_SUBCOLS + D_COLS
TOTAL_COL = "Ergebnis"
COLS_TO_SAVE = ["id_routine"] + SCORE_COLS + ["Ergebnis"]

ROUTINE_RESULT_WEIGHTS = {"T": 0.45, "P": 0.45, "D": 0.10}

EMPTY_SCORE = "–"
LOCKED_D_JUDGE_COLS = ["D3", "D4"]
LOCKED_D_CATEGORIES = ["individual", "pair"]

MIN_SCORE = 0
MAX_D_SCORE = 999
MAX_TP_SCORE = 10

CATEGORY_COL = "category"
POINTS_DB_NAME = "points.db"
POINTS_TABLE_NAME = "points"

COLUMN_LABELS = {
    "routine_name": "Kür-Name",
    "names": "Namen*",
    "age_group": "Altersklasse",
    "category_label": "Kategorie",
    "Ergebnis": "Ergebnis",
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

CATEGORY_JUDGES = {
    "individual female": {
        "T": ["T1", "T2", "T3", "T4"],
        "P": ["P1", "P2", "P3", "P4"],
        "D": ["D1", "D2"],
    },
    "individual male": {
        "T": ["T1", "T2", "T3", "T4"],
        "P": ["P1", "P2", "P3", "P4"],
        "D": ["D1", "D2"],
    },
    "pair": {
        "T": ["T1", "T2", "T3", "T4"],
        "P": ["P1", "P2", "P3", "P4"],
        "D": ["D1", "D2"],
    },
    "small_group": {
        "T": ["T1", "T2", "T3", "T4"],
        "P": ["P1", "P2", "P3", "P4"],
        "D": ["D1", "D2", "D3", "D4"],
    },
    "large_group": {
        "T": ["T1", "T2", "T3", "T4"],
        "P": ["P1", "P2", "P3", "P4"],
        "D": ["D1", "D2", "D3", "D4"],
    },
}

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

def get_project_paths():
    """Construct and return important project-related filesystem paths.

    Paths are resolved relative to the current file location using __file__,
    ensuring stable behavior regardless of the working directory.

    :return Paths: Dataclass containing script directory, config file path,
        and project root directory.
    """
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent

    return {
        "script_dir": script_dir,
        "config_path": script_dir / "config.json",
        "project_root": project_root,
    }


def load_config(config_path: Path):
    """Load application configuration from a JSON file.

    :param Path config_path: Path to the configuration JSON file.
    :return dict: Parsed configuration data as a dictionary.
    """
    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)

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
        self.paths = get_project_paths()
        self.config = load_config(self.paths["config_path"])
        self.stored_hash = self.config["jury_password_hash"].encode()

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

    # ----------------- Path -----------------
    def _db_path(self, name: str):
        """Return the path to a database file located in the project's data folder.

        :param str name: Name of the database file (e.g., "points.db").
        :return Path: Path object pointing to the requested database file.
        """
        return self.paths["project_root"] / "data" / name

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
        """Generate a column definition for judge score columns.

        :param str col: Column identifier (e.g., "T1_Q").
        :param bool jury_mode: Whether jury mode is active (editable scores).
        :return dict: Dash DataTable column configuration dictionary.
        """
        judge, sub = col.split("_", 1)

        return {
            "name": [judge, sub],
            "id": col,
            "type": "numeric",
            "editable": jury_mode,
        }

    def _judge_legend_collapsible(self, theme):
        """Build a collapsible legend explaining judge scoring categories.

        :param dict theme: Active theme color configuration.
        :return html.Div: Container with toggle button and legend content.
        """

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
            """Create a legend column for a specific judge category.

            :param str judge: Judge category identifier (e.g., "T", "P", "D").
            :param dict subs: Dictionary mapping subcategory codes to description text.
            :return html.Div: Dash container with header and formatted legend entries.
            """
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

    def _apply_locked_d_judges(self, df):
        """Lock D3/D4 judges for non-group categories by setting values to "–".

        :param pd.DataFrame df: Dataframe containing all routine scores.
        :return pd.DataFrame: Updated dataframe with D3/D4 cleared where not allowed.
        """
        df = df.copy()
        locked_categories = {"individual female", "individual male", "pair"}

        if "category" not in df.columns:
            return df

        for category in locked_categories:
            mask = df["category"] == category
            for sub in D_SUBS:
                df.loc[mask, f"D3_{sub}"] = "–"
                df.loc[mask, f"D4_{sub}"] = "–"

        return df

    def _coerce_score_columns(self, df):
        """Convert score columns to numeric values, treating "–" as missing.

        :param pd.DataFrame df: Dataframe containing routine scores.
        :return pd.DataFrame: Dataframe with score columns converted to numeric dtype.
        """
        df = df.copy()

        for col in SCORE_COLS:
            if col not in df.columns:
                df[col] = np.nan
            df[col] = pd.to_numeric(df[col].replace("–", np.nan), errors="coerce")

        return df

    def calculate_result(self, df_points, category, age_group):
        """Calculate normalized routine results for one category and age group.

        Scores are summed per judge, converted to percentages across all routines,
        averaged per domain (T, P, D), and combined into Ergebnis using weights.

        :param pd.DataFrame df_points: Full dataframe containing all routines and scores.
        :param str category: Routine category (e.g. individual, pair, group).
        :param str age_group: Age group of the routines.
        :return pd.DataFrame: Result dataframe indexed by id_routine with columns
            T, P, D, Ergebnis.
        """
        category_judges = CATEGORY_JUDGES.get(category)
        if not category_judges:
            return pd.DataFrame(columns=["T", "P", "D", "Ergebnis"])

        group_df = df_points[
            (df_points["category"] == category) & (df_points["age_group"] == age_group)
        ].copy()

        if group_df.empty:
            return pd.DataFrame(columns=["T", "P", "D", "Ergebnis"])

        group_df = self._apply_locked_d_judges(group_df)
        group_df = self._coerce_score_columns(group_df)
        group_df = group_df.set_index("id_routine", drop=True)

        per_judge = pd.DataFrame(index=group_df.index)

        for judge_domain in ["T", "P", "D"]:
            for judge in category_judges[judge_domain]:
                judge_columns = [
                    col for col in group_df.columns if col.startswith(f"{judge}_")
                ]
                if judge_columns:
                    per_judge[judge] = group_df[judge_columns].sum(axis=1, skipna=True)

        percentage_per_routine_per_judge = per_judge.copy()
        for judge in percentage_per_routine_per_judge.columns:
            judge_total = percentage_per_routine_per_judge[judge].sum()
            if pd.isna(judge_total) or judge_total == 0:
                percentage_per_routine_per_judge[judge] = 0.0
            else:
                percentage_per_routine_per_judge[judge] = (
                    percentage_per_routine_per_judge[judge] / judge_total
                )

        result = pd.DataFrame(index=group_df.index, columns=["T", "P", "D", "Ergebnis"])

        for judge_domain in ["T", "P", "D"]:
            relevant_judges = [
                judge
                for judge in category_judges[judge_domain]
                if judge in percentage_per_routine_per_judge.columns
            ]
            if relevant_judges:
                result[judge_domain] = percentage_per_routine_per_judge[relevant_judges].mean(axis=1)
            else:
                result[judge_domain] = 0.0

        result["Ergebnis"] = (
            result["T"] * ROUTINE_RESULT_WEIGHTS["T"]
            + result["P"] * ROUTINE_RESULT_WEIGHTS["P"]
            + result["D"] * ROUTINE_RESULT_WEIGHTS["D"]
        )*100

        return result

    def recalculate_all_results(self, df):
        """Recalculate results for all routines grouped by category and age group.

        :param pd.DataFrame df: Dataframe containing all routines and scores.
        :return pd.DataFrame: Updated dataframe with recalculated result columns.
        """
        df = df.copy()

        result_cols = ["T", "P", "D", "Ergebnis"]
        for col in result_cols:
            if col not in df.columns:
                df[col] = np.nan
            df[col] = pd.to_numeric(df[col], errors="coerce").astype(float)

        for (category, age_group), _ in df.groupby(["category", "age_group"], dropna=False):
            result_df = self.calculate_result(df, category, age_group)
            if result_df.empty:
                continue

            result_df = result_df.astype(float).round(2)

            for routine_id, values in result_df.iterrows():
                mask = df["id_routine"] == routine_id
                df.loc[mask, "T"] = values["T"]
                df.loc[mask, "P"] = values["P"]
                df.loc[mask, "D"] = values["D"]
                df.loc[mask, "Ergebnis"] = values["Ergebnis"]

        return df

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
        ordered_cols = base_cols + T_COLS + P_COLS + D_COLS + ["Ergebnis"]

        if jury_mode:
            df_routines = DataLoader(
                self._db_path("routines.db"), "routines"
            ).get_data()

            df_points = DataLoader(
                self._db_path("points.db"), "points"
            ).get_data()

            if df_points.empty:
                df_points = pd.DataFrame(columns=COLS_TO_SAVE)

            df = df_routines.merge(
                df_points,
                on="id_routine",
                how="left",
                suffixes=("", "_points"),
            )

            for col in ["routine_name", "age_group", "category"]:
                points_col = f"{col}_points"
                if points_col in df.columns:
                    df = df.drop(columns=points_col)

            df = self._apply_locked_d_judges(df)

            for col in SCORE_COLS:
                if col not in df.columns:
                    df[col] = np.nan

            df = self.recalculate_all_results(df)

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

            if col == "id_routine":
                continue

            if col in SCORE_COLS:
                columns.append(self._judge_column(col, jury_mode))

            elif col == "Ergebnis":
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
                    "if": {"column_id": "Ergebnis"},
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

            correct_password_hash = self.stored_hash

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
            """Toggle visibility of the jury legend section.

            :param int n_clicks: Number of times the toggle button was clicked.
            :param dict current_style: Current style dictionary of the legend container.
            :return tuple[dict, str]: Updated style dictionary and new button label text.
            """
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
            """Update theme, view mode, titles, modal styling, and table content.

            :param bool is_dark: Whether dark theme is enabled.
            :param bool jury_access: Whether jury mode is active.
            :return tuple[
                dict,        # page-container style
                object,      # table-container children (DataTable or Div)
                str,         # page title
                str,         # view switch button text
                dict,        # view switch button style
                str,         # theme icon
                dict,        # modal header style
                dict,        # modal body style
                dict,        # modal footer style
                dict         # password input style
            ]: Updated UI state and styling components.
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
                    self._db_path("routines.db"), "routines"
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
                    self._db_path("riders.db"), "riders"
                ).get_data(sql_query="SELECT id_rider,name,club FROM riders")
                df_routines = DataLoader(
                    self._db_path("routines.db"), "routines"
                ).get_data(
                    sql_query="SELECT id_routine,routine_name,category,age_group FROM routines"
                )
                df_riders2routines = DataLoader(
                    self._db_path("riders_routines.db"),
                    "riders_routines",
                ).get_data()
                df_display = df_riders2routines.merge(
                    df_riders, on="id_rider", how="left"
                ).merge(
                    df_routines, on="id_routine", how="left"
                )

                df_display = df_display.groupby("id_routine", as_index=False).agg(
                    routine_name=("routine_name", "first"),
                    category=("category", "first"),
                    age_group=("age_group", "first"),
                    names=("name", lambda x: ", ".join(x.dropna().astype(str))),
                )

                df_display = df_display.drop(columns="id_routine")
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
            Input("data-table", "data_timestamp"),
            State("data-table", "data"),
            prevent_initial_call=True,
        )
        def update_points(timestamp, rows):
            """Validate edited scores, recompute totals, and persist to database.

            :param int timestamp: Timestamp of the latest table edit.
            :param list[dict] rows: Updated table rows from DataTable.
            :return list[dict]: Updated table data with clamped values and totals.
            """
            if timestamp is None or not rows:
                raise dash.exceptions.PreventUpdate

            df = pd.DataFrame(rows)

            for col in SCORE_COLS:
                if col not in df.columns:
                    df[col] = np.nan

            def _is_locked_d_judge(category, colname):
                """Check whether a D judge column is locked for a given category.

                :param str category: Category of the routine.
                :param str colname: Name of the score column.
                :return bool: True if the column is locked for the category.
                """
                return (
                        colname in LOCKED_D_JUDGE_COLS
                        and category in LOCKED_D_CATEGORIES
                )

            def _parse_score_value(value):
                """Convert a score input to float if possible.

                :param Any value: Raw cell value from the table.
                :return float | str | float("nan"): Parsed score, EMPTY_SCORE, or NaN.
                """
                if value == EMPTY_SCORE:
                    return EMPTY_SCORE

                try:
                    return float(value)
                except (TypeError, ValueError):
                    return np.nan

            def _validate_d_score(value):
                """Validate a D score.

                :param float value: Parsed numeric score.
                :return int | float("nan"): Validated integer D score or NaN.
                """
                if value < MIN_SCORE:
                    return np.nan
                if value > MAX_D_SCORE or not value.is_integer():
                    return np.nan
                return int(value)

            def _validate_tp_score(value):
                """Validate a technical or performance score.

                :param float value: Parsed numeric score.
                :return float | float("nan"): Validated score or NaN.
                """
                if value < MIN_SCORE:
                    return np.nan
                if value > MAX_TP_SCORE:
                    return np.nan
                return value

            def clamp_cell(value, category, colname):
                """Validate and normalize a score cell value.

                :param Any value: Raw cell value.
                :param str category: Category of the routine.
                :param str colname: Name of the score column.
                :return str | int | float | float("nan"): Normalized score value.
                """
                if _is_locked_d_judge(category, colname):
                    return EMPTY_SCORE

                parsed_value = _parse_score_value(value)
                if parsed_value == EMPTY_SCORE or pd.isna(parsed_value):
                    return parsed_value

                if colname in D_COLS:
                    return _validate_d_score(parsed_value)

                return _validate_tp_score(parsed_value)

            if CATEGORY_COL not in df.columns:
                df[CATEGORY_COL] = None

            for col in SCORE_COLS:
                df[col] = df.apply(
                    lambda row: clamp_cell(row.get(col), row.get(CATEGORY_COL), col),
                    axis=1,
                )

            df = self.recalculate_all_results(df)

            columns_to_save = ["id_routine"] + SCORE_COLS + ["Ergebnis"]

            try:
                DataLoader(
                    self._db_path("points.db"), "points"
                ).update_data(df, columns=columns_to_save)
            except Exception as e:
                print("Error saving points:", e)

            return df.to_dict("records")

    def run(self):
        """Start the Dash development server.

        :return None: Runs the Dash app with debug mode enabled.
        """
        self.app.run(debug=True)


if __name__ == "__main__":
    Dashboard().run()
