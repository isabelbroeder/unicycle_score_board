import datetime
import os
from enum import StrEnum
from pathlib import Path


DATE_COMPETITION = datetime.date(2026, 3, 7)

CELL_WITH_CLUB = (7, "E")

class Categories(StrEnum):
     INDIVIDUAL = "individual"
     PAIR = "pair"
     SMALL_GROUP = "small_group"
     LARGE_GROUP = "large_group"

"""Application-wide constants for the dashboard."""

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
COLS_TO_SAVE = ["id_routine"] + SCORE_COLS + [TOTAL_COL]

ROUTINE_RESULT_WEIGHTS = {"T": 0.45, "P": 0.45, "D": 0.10}

EMPTY_SCORE = "–"
LOCKED_D_JUDGE_COLS = ["D3", "D4"]
LOCKED_D_CATEGORIES = ["individual female", "individual male", "pair"]

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

# the following lines should not be executed on module level as it is doing IO operations (reading a file)
# which happens when ever this module is loaded, not even if something is run.
# Therefore, please move it in a function
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")
UNICYCLE_SCORE_BOARD_PATH = Path(SCRIPT_DIR).parent.parent
LIGHT_THEME = {
    "backgroundColor": "#ffffff",
    "textColor": "#000000",
    "headerBg": "#f0f0f0",
    "headerColor": "#000000",
    "cellBg": "#ffffff",
    "oddRowBg": "#f9f9f9",
    "border": "#dddddd",
}

DARK_THEME = {
    "backgroundColor": "#1e1e1e",
    "textColor": "#ffffff",
    "headerBg": "#333333",
    "headerColor": "#ffffff",
    "cellBg": "#222222",
    "oddRowBg": "#2a2a2a",
    "border": "#444444",
}