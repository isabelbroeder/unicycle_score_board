"""Creates dashboard from data in database."""

import json
from pathlib import Path
from load_data import DataLoader
from src.unicycle.constants import *
from src.unicycle.riders_db_handler import RidersDbHandler
from src.unicycle.routines_db_handler import RoutinesDbHandler
from src.unicycle.riders_routines_db_handler import RidersRoutinesDbHandler
from src.unicycle.points_db_handler import PointsDbHandler
import dash_bootstrap_components as dbc
from dash import Dash

from callbacks import register_callbacks
from components import build_layout
from data_service import DataService


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
    """Load application configuration from a JSON file."""
    with config_path.open("r", encoding="utf-8") as file:
        return json.load(file)


class Dashboard:
    """Main application class for the unicycle scoring dashboard."""

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
