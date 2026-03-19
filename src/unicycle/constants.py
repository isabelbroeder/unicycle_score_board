import datetime
import os
from pathlib import Path


DATE_COMPETITION = datetime.datetime(2026, 3, 7, 0, 0)

CATEGORIES = ["individual", "pair", "small_group", "large_group"]

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
        "S": "Leichte Abstiege",
        "B": "Schwere Abstiege",
        "N": "Anzahl der Fahrer:innen",
    },
}

# the following lines should not be executed on module level as it is doing IO operations (reading a file)
# which happens when ever this module is loaded, not even if something is run.
# Therefore, please move it in a function
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")
UNICYCLE_SCORE_BOARD_PATH = Path(SCRIPT_DIR).parent.parent