"""UI components and layout builders for the dashboard."""

import dash_bootstrap_components as dbc
import dash_daq as daq
import pandas as pd
from dash import dash_table, dcc, html

from constants import (
    BASE_COLS_JURY,
    BASE_COLS_PARTICIPANT,
    CATEGORY_LABELS,
    CATEGORY_ORDER,
    COLUMN_LABELS,
    D_COLS,
    JUDGE_LEGEND,
    P_COLS,
    SCORE_COLS,
    T_COLS,
)


def build_layout():
    """Construct and return the root Dash layout container."""
    return html.Div(
        id="page-container",
        style={
            "minHeight": "100vh",
            "padding": "30px",
            "fontFamily": "Arial, sans-serif",
            "position": "relative",
        },
        children=[
            html.Div(
                [
                    html.Span(
                        "🌞",
                        id="theme-icon",
                        style={"fontSize": "22px", "marginRight": "8px"},
                    ),
                    daq.ToggleSwitch(
                        id="theme-toggle",
                        value=True,
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
                },
            ),
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
            dcc.Store(id="jury-access", data=False),
            dbc.Modal(
                [
                    dbc.ModalHeader("🔒 Jury-Zugang", id="password-modal-header"),
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
                        id="password-modal-body",
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
                        id="password-modal-footer",
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


def build_judge_column(col: str, jury_mode: bool) -> dict:
    """Generate a column definition for judge score columns."""
    judge, sub = col.split("_", 1)
    return {
        "name": [judge, sub],
        "id": col,
        "type": "numeric",
        "editable": jury_mode,
    }


def build_judge_legend_collapsible(theme: dict):
    """Build a collapsible legend explaining judge scoring categories."""
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

    def build_column(judge: str, subs: dict):
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
                        html.Span(label, style={"fontWeight": "bold"}),
                        html.Div(text, style={"fontSize": "13px", "opacity": "0.8"}),
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
                style={**container_style, "display": "none"},
            ),
        ]
    )


def build_datatable(
    df: pd.DataFrame,
    theme: dict,
    editable: bool = False,
    jury_mode: bool = False,
):
    """Create a Dash DataTable configured for participant or jury mode."""
    if df.empty:
        return html.Div(
            "❌ Keine Daten geladen.",
            style={
                "color": "#ff6b6b",
                "textAlign": "center",
                "marginTop": "50px",
            },
        )

    dropdown = {}
    base_cols = BASE_COLS_JURY if jury_mode else BASE_COLS_PARTICIPANT
    ordered_cols = base_cols + T_COLS + P_COLS + D_COLS + ["Ergebnis"]

    if "category" in df.columns:
        df = df.copy()
        df["category_label"] = df["category"].map(CATEGORY_LABELS).fillna(
            df["category"]
        )
        df["category_label"] = pd.Categorical(
            df["category_label"],
            categories=CATEGORY_ORDER,
            ordered=True,
        )
        df = df.sort_values(["category_label", "age_group"])

    columns = []
    for col in ordered_cols:
        if col not in df.columns or col == "id_routine":
            continue

        if col in SCORE_COLS:
            columns.append(build_judge_column(col, jury_mode))
        elif col == "Ergebnis":
            columns.append(
                {
                    "name": ["", COLUMN_LABELS.get(col, col)],
                    "id": col,
                    "type": "numeric",
                    "editable": False,
                }
            )
        else:
            display_col = "category_label" if col == "category" else col
            label = COLUMN_LABELS.get(display_col, display_col)
            columns.append(
                {
                    "name": label if not jury_mode else ["", label],
                    "id": display_col,
                    "editable": False,
                }
            )

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
            {"if": {"column_id": "age_group"}, "textAlign": "center"},
            {"if": {"column_id": "category_label"}, "textAlign": "center"},
            {"if": {"column_type": "numeric"}, "textAlign": "center"},
            {
                "if": {"column_id": "Ergebnis"},
                "textAlign": "right",
                "fontWeight": "bold",
            },
        ],
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": theme["oddRowBg"]},
            *[
                {
                    "if": {
                        "filter_query": (
                            "{category} = 'individual female' || "
                            "{category} = 'individual male' || "
                            "{category} = 'pair'"
                        ),
                        "column_id": col,
                    },
                    "pointerEvents": "none",
                    "backgroundColor": "#444",
                    "color": "#888",
                }
                for col in D_COLS
                if col.startswith(("D3_", "D4_"))
            ],
        ],
    )

    if not jury_mode:
        return html.Div(
            [
                table,
                html.Div(
                    (
                        "* Bei Klein- und Großgruppen wird statt der Namen "
                        "die Anzahl der Teilnehmer angezeigt."
                    ),
                    style={
                        "marginTop": "10px",
                        "fontSize": "12px",
                        "opacity": "0.8",
                    },
                ),
            ]
        )

    return table


def build_dashboard_table(df: pd.DataFrame, theme: dict, jury_mode: bool):
    """Build the table area for the selected view."""
    if jury_mode:
        legend = build_judge_legend_collapsible(theme)
        return html.Div(
            [
                legend,
                build_datatable(df, theme, editable=True, jury_mode=True),
            ]
        )

    return build_datatable(df, theme, editable=False, jury_mode=False)