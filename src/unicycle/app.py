"""Creates dashboard from data in database."""

import json
from src.unicycle.constants import *
import dash_bootstrap_components as dbc
from dash import Dash

from src.unicycle.dashboard.callbacks import register_callbacks
from src.unicycle.dashboard.components import build_layout
from src.unicycle.dashboard.data_service import DataService


def get_project_paths() -> dict[str, Path]:
    """Construct and return important project-related filesystem paths."""
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent

    return {
        "script_dir": script_dir,
        "config_path": script_dir / "config.json",
        "project_root": project_root,
    }


def load_config(config_path: Path) -> dict:
    """Load dashboard configuration from a JSON file."""
    with config_path.open("r", encoding="utf-8") as file:
        return json.load(file)


class Dashboard:
    """Main dashboard class for the unicycle scoring dashboard."""

    def __init__(self):
        self.app = Dash(
            __name__,
            title="Fahrerinnen & Jury Dashboard",
            suppress_callback_exceptions=True,
            external_stylesheets=[dbc.themes.DARKLY],
        )
        self.paths = get_project_paths()
        self.config = load_config(self.paths["config_path"])
        self.stored_hash = self.config["jury_password_hash"].encode()
        self.data_service = DataService(self.paths["project_root"])

        self.app.layout = build_layout()
        register_callbacks(self.app, self.data_service, self.stored_hash)

    def run(self):
        """Start the Dash development server."""
        self.app.run(debug=True)


if __name__ == "__main__":
    Dashboard().run()
