"""Scoring and validation logic for the dashboard."""

import numpy as np
import pandas as pd

from src.unicycle.constants import (
    CATEGORY_COL,
    CATEGORY_JUDGES,
    D_COLS,
    D_SUBS,
    EMPTY_SCORE,
    LOCKED_D_CATEGORIES,
    LOCKED_D_JUDGE_COLS,
    MAX_D_SCORE,
    MAX_TP_SCORE,
    MIN_SCORE,
    ROUTINE_RESULT_WEIGHTS,
    SCORE_COLS,
)

RESULT_COLS = ["T", "P", "D", "Ergebnis"]
GROUP_CATEGORIES = {
    "small_group",
    "large_group",
}


def apply_locked_d_judges(df: pd.DataFrame) -> pd.DataFrame:
    """Set locked D3 and D4 judge fields to the empty-score marker.

    pd.DataFrame df: Score dataframe whose locked D columns should be normalized.
    """
    df = df.copy()

    if CATEGORY_COL not in df.columns:
        return df

    for category in LOCKED_D_CATEGORIES:
        mask = df[CATEGORY_COL] == category
        for sub in D_SUBS:
            df.loc[mask, f"D3_{sub}"] = EMPTY_SCORE
            df.loc[mask, f"D4_{sub}"] = EMPTY_SCORE

    return df


def coerce_score_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Convert score columns to numeric values where possible.

    pd.DataFrame df: Score dataframe whose score columns should be coerced.
    """
    df = df.copy()

    for col in SCORE_COLS:
        if col not in df.columns:
            df[col] = np.nan
        df[col] = pd.to_numeric(
            df[col].replace(EMPTY_SCORE, np.nan),
            errors="coerce",
        )

    return df


def calculate_result(
    df_points: pd.DataFrame,
    category: str,
    age_group: str,
) -> pd.DataFrame:
    """Calculate normalized results for one category and age group.

    pd.DataFrame df_points: Full scoring dataframe containing all routines.
    str category: Routine category whose results should be calculated.
    str age_group: Age group whose results should be calculated.
    """
    category_judges = CATEGORY_JUDGES.get(category)
    if not category_judges:
        return pd.DataFrame(columns=RESULT_COLS)

    group_df = df_points[
        (df_points[CATEGORY_COL] == category) & (df_points["age_group"] == age_group)
    ].copy()

    if group_df.empty:
        return pd.DataFrame(columns=RESULT_COLS)

    group_df = apply_locked_d_judges(group_df)
    group_df = coerce_score_columns(group_df)
    group_df = group_df.set_index("id_routine", drop=True)

    per_judge = pd.DataFrame(index=group_df.index)

    for judge_domain in ["T", "P"]:
        for judge in category_judges[judge_domain]:
            judge_columns = [
                col for col in group_df.columns if col.startswith(f"{judge}_")
            ]
            if judge_columns:
                per_judge[judge] = group_df[judge_columns].sum(
                    axis=1,
                    min_count=1,
                )

    for judge in category_judges["D"]:
        s_col = f"{judge}_S"
        b_col = f"{judge}_B"
        n_col = f"{judge}_N"

        if s_col not in group_df.columns or b_col not in group_df.columns:
            continue

        s_values = group_df[s_col]
        b_values = group_df[b_col]
        has_d_input = s_values.notna() | b_values.notna()

        divisor = 1.0
        if category in GROUP_CATEGORIES:
            if n_col in group_df.columns:
                n_values = group_df[n_col]
                divisor = np.sqrt(n_values.where(n_values > 0))
            else:
                divisor = np.nan

        raw_d_score = 10 - ((s_values * 0.5 + b_values) / divisor)
        raw_d_score = raw_d_score.where(has_d_input, np.nan)

        valid_raw = raw_d_score.dropna()
        if not valid_raw.empty:
            shift = min(valid_raw.min(), 0)
            adjusted_d_score = raw_d_score - shift
        else:
            adjusted_d_score = raw_d_score

        per_judge[judge] = adjusted_d_score

    percentage_per_routine_per_judge = per_judge.copy()

    for judge in percentage_per_routine_per_judge.columns:
        judge_scores = percentage_per_routine_per_judge[judge]
        valid_mask = judge_scores.notna()

        if not valid_mask.any():
            percentage_per_routine_per_judge[judge] = np.nan
            continue

        judge_total = judge_scores[valid_mask].sum()

        if judge_total == 0:
            percentage_per_routine_per_judge[judge] = np.nan
            percentage_per_routine_per_judge.loc[valid_mask, judge] = (
                1.0 / valid_mask.sum()
            )
        else:
            percentage_per_routine_per_judge[judge] = judge_scores / judge_total

    result = pd.DataFrame(index=group_df.index, columns=RESULT_COLS)

    for judge_domain in ["T", "P", "D"]:
        relevant_judges = [
            judge
            for judge in category_judges[judge_domain]
            if judge in percentage_per_routine_per_judge.columns
        ]

        if not relevant_judges:
            result[judge_domain] = np.nan
            continue

        domain_scores = percentage_per_routine_per_judge[relevant_judges].mean(
            axis=1,
            skipna=True,
        )
        valid_mask = domain_scores.notna()

        if not valid_mask.any():
            result[judge_domain] = np.nan
            continue

        domain_total = domain_scores[valid_mask].sum()

        if domain_total == 0:
            result[judge_domain] = np.nan
            result.loc[valid_mask, judge_domain] = 1.0 / valid_mask.sum()
        else:
            result[judge_domain] = domain_scores / domain_total

    available_weight = (
        result["T"].notna().astype(float) * ROUTINE_RESULT_WEIGHTS["T"]
        + result["P"].notna().astype(float) * ROUTINE_RESULT_WEIGHTS["P"]
        + result["D"].notna().astype(float) * ROUTINE_RESULT_WEIGHTS["D"]
    )

    weighted_sum = (
        result["T"].fillna(0) * ROUTINE_RESULT_WEIGHTS["T"]
        + result["P"].fillna(0) * ROUTINE_RESULT_WEIGHTS["P"]
        + result["D"].fillna(0) * ROUTINE_RESULT_WEIGHTS["D"]
    )

    result["Ergebnis"] = np.where(
        available_weight > 0,
        (weighted_sum / available_weight) * 100,
        np.nan,
    )

    has_any_result = result[["T", "P", "D"]].notna().any(axis=1)
    result["Ergebnis"] = result["Ergebnis"].where(has_any_result, np.nan)

    return result


def recalculate_all_results(df: pd.DataFrame) -> pd.DataFrame:
    """Recompute result columns for all category and age-group combinations.

    pd.DataFrame df: Score dataframe whose result columns should be refreshed.
    """
    df = df.copy()

    for col in RESULT_COLS:
        if col not in df.columns:
            df[col] = np.nan
        df[col] = pd.to_numeric(df[col], errors="coerce").astype(float)

    result_frames = []

    for (category, age_group), _ in df.groupby(
        [CATEGORY_COL, "age_group"],
        dropna=False,
    ):
        result_df = calculate_result(df, category, age_group)
        if result_df.empty:
            continue

        result_df = result_df.astype(float).round(2).reset_index()
        result_frames.append(result_df)

    if result_frames:
        all_results = pd.concat(result_frames, ignore_index=True)
        df = df.drop(columns=RESULT_COLS, errors="ignore").merge(
            all_results,
            on="id_routine",
            how="left",
        )

    return df


def is_locked_d_judge(category: str, colname: str) -> bool:
    """Check whether a D-judge column is locked for the given category.

    str category: Routine category being validated.
    str colname: Score column name whose lock status should be checked.
    """
    judge_prefix = str(colname).split("_", 1)[0]
    return judge_prefix in LOCKED_D_JUDGE_COLS and category in LOCKED_D_CATEGORIES


def parse_score_value(value):
    """Parse a raw score cell value into a normalized numeric form.

    Any value: Raw score cell value entered in the dashboard table.
    """
    if value == EMPTY_SCORE:
        return EMPTY_SCORE

    try:
        return float(value)
    except (TypeError, ValueError):
        return np.nan


def validate_d_score(value: float):
    """Validate a difficulty score value.

    float value: Parsed difficulty score to validate.
    """
    if value > MAX_D_SCORE or not value.is_integer():
        return np.nan
    return int(value)


def validate_tp_score(value: float):
    """Validate a technical or performance score value.

    float value: Parsed T or P score to validate.
    """
    if value < MIN_SCORE:
        return np.nan
    if value > MAX_TP_SCORE:
        return np.nan
    return value


def clamp_cell(value, category: str, colname: str):
    """Normalize and validate one score cell value for table persistence.

    Any value: Raw score cell value entered in the dashboard table.
    str category: Routine category used to determine locking rules.
    str colname: Score column name used to determine validation rules.
    """
    if is_locked_d_judge(category, colname):
        return EMPTY_SCORE

    parsed_value = parse_score_value(value)
    if parsed_value == EMPTY_SCORE or pd.isna(parsed_value):
        return parsed_value

    if colname in D_COLS:
        return validate_d_score(parsed_value)

    return validate_tp_score(parsed_value)
