"""Dash callback registration for the dashboard."""

import bcrypt
import dash
import numpy as np
import pandas as pd
from dash import Input, Output, State

from components import build_dashboard_table
from constants import CATEGORY_COL, DARK_THEME, LIGHT_THEME, SCORE_COLS
from scoring import clamp_cell, recalculate_all_results


def register_callbacks(app, data_service, stored_hash: bytes):
    """Register all Dash callbacks for UI interactivity and persistence."""

    @app.callback(
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
        cancel_clicks,
        enter_submit,
        is_open,
        password,
        has_access,
    ):
        del open_clicks, submit_clicks, cancel_clicks, enter_submit, is_open

        ctx = dash.callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if button_id == "view-switch-btn":
            if has_access:
                return False, "", "", False
            return True, "", "", False

        if button_id in ("submit-password", "password-input"):
            if password and bcrypt.checkpw(password.encode(), stored_hash):
                return False, "", "", True
            return True, "❌ Falsches Passwort!", "", False

        if button_id == "cancel-password":
            return False, "", "", has_access

        raise dash.exceptions.PreventUpdate

    @app.callback(
        Output("legend-container", "style"),
        Output("legend-toggle-btn", "children"),
        Input("legend-toggle-btn", "n_clicks"),
        State("legend-container", "style"),
        prevent_initial_call=True,
    )
    def toggle_legend(n_clicks, current_style):
        del n_clicks

        visible = current_style.get("display") == "block"
        new_display = "none" if visible else "block"
        button_text = (
            "📖 Jury-Kategorien anzeigen"
            if visible
            else "📖 Jury-Kategorien ausblenden"
        )
        current_style["display"] = new_display
        return current_style, button_text

    @app.callback(
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
        theme = DARK_THEME if is_dark else LIGHT_THEME
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
            df_view = data_service.load_jury_view_data()
            title = "⚖️ Jury Übersicht"
            button_text = "👥 Wechsel zu Teilnehmer Ansicht"
        else:
            df_view = data_service.load_participant_view_data()
            title = "🏁 Teilnehmer Übersicht"
            button_text = "⚖️ Wechsel zu Jury Ansicht"

        table = build_dashboard_table(df_view, theme, jury_mode=jury_mode)

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

    @app.callback(
        Output("data-table", "data", allow_duplicate=True),
        Input("data-table", "data_timestamp"),
        State("data-table", "data"),
        prevent_initial_call=True,
    )
    def update_points(timestamp, rows):
        if timestamp is None or not rows:
            raise dash.exceptions.PreventUpdate

        df = pd.DataFrame(rows)

        for col in SCORE_COLS:
            if col not in df.columns:
                df[col] = np.nan

        if CATEGORY_COL not in df.columns:
            df[CATEGORY_COL] = None

        for col in SCORE_COLS:
            df[col] = df.apply(
                lambda row: clamp_cell(row.get(col), row.get(CATEGORY_COL), col),
                axis=1,
            )

        df = recalculate_all_results(df)

        try:
            data_service.save_points(df)
        except Exception as exc:
            print("Error saving points:", exc)

        return df.to_dict("records")
