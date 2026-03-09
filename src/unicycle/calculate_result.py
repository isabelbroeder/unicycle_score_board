from pathlib import Path
import itertools

import numpy as np
import pandas as pd

from load_data import DataLoader

unicycle_score_board_path = Path(Path.cwd().parent.parent)


def calculate_result(category: str, age_group: str, judges: dict):
    judges = judges[category]
    t_judges = [judge for judge in judges if judge.startswith("T")]
    p_judges = [judge for judge in judges if judge.startswith("P")]
    d_judges = [judge for judge in judges if judge.startswith("D")]

    category = "'" + category + "'"  # must be in single quotes for sql
    age_group = "'" + age_group + "'"

    df_points = DataLoader(
        Path(unicycle_score_board_path, "data/points.db"), "points"
    ).get_data(
        f" SELECT * FROM points WHERE category == {category}  AND age_group == {age_group}"
    )

    df_points.set_index("id_routine", inplace=True, drop=True)
    df_sum_points_per_routine_per_judge = pd.DataFrame(index=df_points.index)

    for judge in itertools.chain(t_judges, p_judges):
        columns = (df_points.columns[
            df_points.columns.str.contains(judge)])
        df_sum_points_per_routine_per_judge[judge] = df_points[
            columns].sum(axis=1)

    divisor = 1
    for d_judge in d_judges:
        if category == "Small Group" or category == "Large Group":
            divisor = np.sqrt(df_points[f"{d_judge}_N"])
        df_sum_points_per_routine_per_judge[f"{d_judge}"] = 10 - (
                    df_points[f"{d_judge}_S"] * 0.5 + df_points[f"{d_judge}_B"] / divisor)

    percentage_per_routine_per_judge = df_sum_points_per_routine_per_judge.div(
        df_sum_points_per_routine_per_judge.sum(axis=0)) * 100
    print(percentage_per_routine_per_judge)
    result = pd.DataFrame(index=df_points.index,
                          columns=["T", "P", "D", "total"])

    for judge_domain in ["T", "P", "D"]:
        relevant_cols = [
            judge for judge in judges if judge.startswith(judge_domain)
        ]
        result[judge_domain] = percentage_per_routine_per_judge[
            relevant_cols].mean(axis=1)

    f = lambda x: (x['T'] * 0.45 + x['P'] * 0.45 + x['D'] * 0.1)
    result['total'] = result.apply(f, axis=1)
    result["rank"] = result[["total", "T"]].apply(tuple, axis=1).rank(method='min', ascending=False).astype(int)
    return result


def generate_judges(t_p_count, d_count) -> list[str]:
    """
    generates list of judges
    t_count : number of technic judges
    p_count : number of performance judges
    d_count : number of dismount judges
    return: list of abbreviation of the judges like ['T1', 'T2' 'P1', 'P2', 'D1']
    """
    judges_list = []
    for i in range(1, t_p_count + 1):
        judges_list.append(f"T{i}")
        judges_list.append(f"P{i}")
    for i in range(1, d_count + 1):
        judges_list.append(f"D{i}")
    return judges_list


def create_judges():
    # number of judges in each category
    number_t_p_judges = 4
    number_d_judges_individual_pair = 2
    number_d_judges_group = 4
    # Create dictionary
    judges = {
        "individual female":
            generate_judges(number_t_p_judges, number_d_judges_individual_pair),
        "individual male":
            generate_judges(number_t_p_judges, number_d_judges_individual_pair),
        "pair":
            generate_judges(number_t_p_judges, number_d_judges_individual_pair),
        "small_group":
            generate_judges(number_t_p_judges, number_d_judges_group),
        "large_group":
            generate_judges(number_t_p_judges, number_d_judges_group),
    }
    return judges

    # points_routine = df_points[]
    # sum_judge_per_routine =


# judges = create_judges()
# print(judges['single'])
judges = create_judges()
calculate_result("individual female", "U11", judges)
