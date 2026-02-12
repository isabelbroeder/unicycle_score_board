from pathlib import Path
import itertools
import pandas as pd

from load_data import DataLoader

unicycle_score_board_path = Path(Path.cwd().parent.parent)


def calculate_result(category: str, age_group: str, judges: dict):
    judges = judges[category]
    t_judges = [judge for judge in judges if judge.startswith("T")]
    p_judges = [judge for judge in judges if judge.startswith("P")]
    d_judges = [judge for judge in judges if judge.startswith("D")]

    category = "'" + category + "'"  # must be in single quotes for sql
    age_goup = "'" + age_group + "'"

    # read database points
    df_points = DataLoader(
        Path(unicycle_score_board_path, "data/points.db"), "points"
    ).get_data(
        f" SELECT * FROM points WHERE category == {category}  AND age_group == {age_goup}"
    )
    print(df_points.columns)

    df_points.set_index("id_routine", inplace=True, drop=True)
    df_points = df_points.apply(pd.to_numeric, errors="coerce")
    print(df_points.columns)

    # sum points per routine and judge
    df_sum_points_per_routine_per_judge = pd.DataFrame(index=df_points.index)
    print(df_points.columns)

    for judge in itertools.chain(t_judges, p_judges):
        relevant_cols = [f"{judge}_T", f"{judge}_S", f"{judge}_E"]
        df_sum_points_per_routine_per_judge[judge] = df_points[relevant_cols].sum(
            axis=1
        )

    print(df_sum_points_per_routine_per_judge)
    print(df_points.columns)
    # percentage of points per routine and judge
    percentage_per_routine_per_judge = df_sum_points_per_routine_per_judge.div(
        df_sum_points_per_routine_per_judge.sum(axis=0)
    )
    print(percentage_per_routine_per_judge)
    result = pd.DataFrame(index=df_points.index, columns=["T", "P", "D", "total"])

    for judge_domain in ["T", "P"]:
        relevant_cols = [judge for judge in judges if judge.startswith(judge_domain)]
        print(relevant_cols)
        print(percentage_per_routine_per_judge[relevant_cols].mean(axis=1))
        result[judge_domain] = percentage_per_routine_per_judge[relevant_cols].mean(
            axis=1
        )
    print(result)

    # calculate dismounts
    print(df_points.columns)


def generate_judges(t_count, p_count, d_count) -> list[str]:
    """
    generates list of judges
    t_count : number of technic judges
    p_count : number of performance judges
    d_count : number of dismount judges
    return: list of abbreviation of the judges like ['T1', 'T2' 'P1', 'P2', 'D1']
    """
    judges_list = []
    for i in range(1, t_count + 1):
        judges_list.append(f"T{i}")
    for i in range(1, p_count + 1):
        judges_list.append(f"P{i}")
    for i in range(1, d_count + 1):
        judges_list.append(f"D{i}")
    return judges_list


def create_judges():
    # number of judges in each category
    individual_t = 4
    individual_p = 4
    individual_d = 2
    pair_t = 4
    pair_p = 4
    pair_d = 2
    small_group_t = 4
    small_group_p = 4
    small_group_d = 4
    large_group_t = 4
    large_group_p = 4
    large_group_d = 4
    # Create dictionary
    judges = {
        "individual": generate_judges(individual_t, individual_p, individual_d),
        "pair": generate_judges(pair_t, pair_p, pair_d),
        "small_group": generate_judges(small_group_t, small_group_p, small_group_d),
        "large_group": generate_judges(large_group_t, large_group_p, large_group_d),
    }
    return judges

    # points_routine = df_points[]
    # sum_judge_per_routine =


# judges = create_judges()
# print(judges['single'])
judges = create_judges()
calculate_result("individual", "U21", judges)
