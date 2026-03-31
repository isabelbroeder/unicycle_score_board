"""Creates dashboard from data in database."""

from src.unicycle.constants import *
import dash_bootstrap_components as dbc
from dash import Dash

from src.unicycle.dashboard.callbacks import register_callbacks
from src.unicycle.dashboard.components import build_layout
from src.unicycle.dashboard.data_service import DataService


class Dashboard:
    """Main dashboard class for the unicycle scoring dashboard."""

    def __init__(self):
        self.app = Dash(
            __name__,
            title="Fahrerinnen & Jury Dashboard",
            suppress_callback_exceptions=True,
            external_stylesheets=[dbc.themes.DARKLY],
        )
        self.config = load_config(get_path_config_file())
        self.stored_hash = self.config["jury_password_hash"].encode()
        self.data_service = DataService(get_path_project_root())

        self.app.layout = build_layout()
        register_callbacks(self.app, self.data_service, self.stored_hash)

    def run(self):
        """Start the Dash development server."""
        self.app.run(debug=True)


if __name__ == "__main__":
    Dashboard().run()
