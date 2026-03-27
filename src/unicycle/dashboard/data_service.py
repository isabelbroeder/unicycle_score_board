"""Data loading and persistence helpers for the dashboard."""

from pathlib import Path

import numpy as np
import pandas as pd

from constants import COLS_TO_SAVE, SCORE_COLS
from scoring import apply_locked_d_judges, recalculate_all_results
from src.unicycle.db_handler.points_db_handler import PointsDbHandler
from src.unicycle.db_handler.riders_db_handler import RidersDbHandler
from src.unicycle.db_handler.routines_db_handler import RoutinesDbHandler
from src.unicycle.db_handler.riders_routines_db_handler import RidersRoutinesDbHandler

POINTS_DB_HANDLER = PointsDbHandler()
RIDERS_DB_HANDLER = RidersDbHandler()
ROUTINES_DB_HANDLER = RoutinesDbHandler()
RIDERSROUTINES_DB_HANDLER = RidersRoutinesDbHandler()

class DataService:
    """Encapsulates all database access used by the dashboard."""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)

    def db_path(self, name: str) -> Path:
        """Return the path to a database file in the data directory."""
        return self.project_root / "data" / name

    def load_routines(self) -> pd.DataFrame:
        """Load all routine records."""
        return ROUTINES_DB_HANDLER.get_data()

    def load_routines_for_participant_view(self) -> pd.DataFrame:
        """Load only the routine columns needed for participant view."""
        return ROUTINES_DB_HANDLER.get_data(
            sql_query=(
                "SELECT id_routine, routine_name, category, age_group "
                "FROM routines"
            )
        )

    def load_riders(self) -> pd.DataFrame:
        """Load rider data used for participant display."""
        return RIDERS_DB_HANDLER.get_data(
            sql_query="SELECT id_rider, name, club FROM riders"
        )

    def load_riders_routines(self) -> pd.DataFrame:
        """Load the rider-to-routine mapping table."""
        return RIDERSROUTINES_DB_HANDLER.get_data()

    def load_points(self) -> pd.DataFrame:
        """Load all persisted scoring data."""
        return POINTS_DB_HANDLER.get_data()

    def load_jury_view_data(self) -> pd.DataFrame:
        """Load and prepare the dataframe used in jury mode."""
        df_routines = self.load_routines()
        df_points = self.load_points()

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

        df = apply_locked_d_judges(df)

        for col in SCORE_COLS:
            if col not in df.columns:
                df[col] = np.nan

        return recalculate_all_results(df)

    def load_participant_view_data(self) -> pd.DataFrame:
        """Load and prepare the dataframe used in participant mode."""
        df_riders = self.load_riders()
        df_routines = self.load_routines_for_participant_view()
        df_riders2routines = self.load_riders_routines()

        df_display = df_riders2routines.merge(
            df_riders,
            on="id_rider",
            how="left",
        ).merge(
            df_routines,
            on="id_routine",
            how="left",
        )

        df_display = df_display.groupby("id_routine", as_index=False).agg(
            routine_name=("routine_name", "first"),
            category=("category", "first"),
            age_group=("age_group", "first"),
            names=("name", lambda x: ", ".join(x.dropna().astype(str))),
        )

        df_display = df_display.drop(columns="id_routine")
        df_display["names"] = df_display.apply(self._format_names, axis=1)
        return df_display

    def save_points(
        self,
        df: pd.DataFrame,
        columns: list[str] | None = None,
    ) -> None:
        """Persist scoring data to the points database."""
        POINTS_DB_HANDLER.update_data(
            df,
            columns=columns or COLS_TO_SAVE,
        )

    @staticmethod
    def _format_names(row: pd.Series) -> str:
        """Format participant names for display in the participant view."""
        if row["category"] in ["small_group", "large_group"] and isinstance(
            row["names"],
            str,
        ):
            count = len(
                [name for name in row["names"].split(",") if name.strip()]
            )
            return f"{count} Personen"
        return row["names"]