import fnmatch
import math
import pandas as pd
import numpy as np


# TODO figure out how to change which args are passed to which scoring function
def calculate_special_survey_scoring(
    df: pd.DataFrame, survey_scoring: dict
) -> pd.DataFrame:
    """Calculates average, total, and category scores with special logic for surveys.

    Arguments:
        df: Data source data frame.
        survey_scoring: Dictionary of survey scoring configurations.

    Returns:
        df: Data frame with calculated scores.
    """
    scoring_method_dict = {
        "normal": score_normal_survey,
        "wai": score_wai_survey,
        "eq5d": score_eq5d_survey,
    }
    for survey, score_config in survey_scoring.items():
        prefix = score_config["question_prefix"]
        method = score_config["scoring_method"]
        skip_questions = score_config.get("skip_questions")
        survey_question_list = fnmatch.filter(list(df.columns), f"{prefix}*")
        if skip_questions:
            survey_question_list = [
                question
                for question in survey_question_list
                if question not in skip_questions
            ]
        if method in scoring_method_dict:
            df = scoring_method_dict[method](
                survey=survey,
                survey_question_list=survey_question_list,
                prefix=prefix,
                df=df,
                survey_scoring=survey_scoring,
            )
        else:
            raise ValueError(f"Survey {survey} is not supported and cannot be scored.")
    return df


def score_normal_survey(
    survey: str,
    survey_question_list: list,
    prefix: str,
    df: pd.DataFrame,
    survey_scoring: dict,
) -> pd.DataFrame:
    """Calculates average, total, and category scores for a survey without special scoreing logic

    Arguments:
        survey: name of the survey form config
        survey_question_list: list of data frame columns that make up the survey questions
        prefix: prefix of df columns that identify this survey's questions
        df: survey data frame
        survey_scoring: dictionary with survey scoring config

    Returns:
        df(pd.Dataframe): final scored dataframe
    """
    average_list = []
    total_list = []
    category_list = []
    for i, row in df.iterrows():
        value_list = []
        for question in survey_question_list:
            value_list.append(float(row[question]))
        total_score = sum(value_list)
        average_score = sum(value_list) / len(value_list)
        total_list.append(total_score)
        average_list.append(average_score)
        # get category value TODO make helper function
    index_list = []
    for i, total in enumerate(total_list):
        for category, limits in survey_scoring[survey]["category"].items():
            if math.isnan(total):
                category_list.append("")
                break
            elif total >= limits[0] and total <= limits[1]:
                category_list.append(category)
                index_list.append(i)
                break
    average_header = f"{prefix}_average_score"
    df[average_header] = average_list
    total_header = f"{prefix}_total_score"
    df[total_header] = total_list
    category_header = f"{prefix}_cat"
    df[category_header] = category_list
    return df


def score_wai_survey(
    survey: str,
    survey_question_list: list,
    prefix: str,
    df: pd.DataFrame,
    survey_scoring: dict,
) -> pd.DataFrame:
    """Calculates average, total, and category scores with special logic for WAI survey

    Arguments:
        survey: name of the survey form config
        survey_question_list: list of data frame columns that make up the survey questions
        prefix: prefix of df columns that identify this survey's questions
        df: survey data frame
        survey_scoring: dictionary with survey scoring config

    Returns:
        df: final scored dataframe
    """
    average_list = []
    total_list = []
    category_list = []
    item_7_dict = {
        0: 1,
        1: 1,
        2: 1,
        3: 1,
        4: 2,
        5: 2,
        6: 2,
        7: 3,
        8: 3,
        9: 3,
        10: 4,
        11: 4,
        12: 4,
    }
    survey_question_list = survey_question_list[1:]
    for _, row in df.iterrows():
        item_7_list = []
        if row["qq_wai_1"] is np.nan:
            average_list.append("")
            total_list.append("")
        else:
            work_type = int(
                row["qq_wai_1"]  # 1 is psychological, 2 is physical, 3 is both
            )
            value_list = []
            for question in survey_question_list:
                response = int(row[question])
                if question == "qq_wai_3":  # physically demanding qustion
                    if work_type == 1 and response in [1, 2]:
                        value_list.append(response * 0.5)
                    elif work_type == 2 and response in [3, 4, 5]:
                        value_list.append(response * 1.5)
                    else:
                        value_list.append(response)
                if question == "qq_wai_4":  # psychologically demanding qustion
                    if work_type == 1 and response in [3, 4, 5]:
                        value_list.append(response * 1.5)
                    elif work_type == 2 and response in [1, 2]:
                        value_list.append(response * 0.5)
                    else:
                        value_list.append(response)
                if question in ["qq_wai_8", "qq_wai_9", "qq_wai_10"]:
                    item_7_list.append(response)
            item_7_total = sum(item_7_list)
            item_7_score = item_7_dict[item_7_total]
            value_list.append(item_7_score)
            average_list.append(sum(value_list) / len(value_list))
            total_list.append(sum(value_list))
    for item in total_list:
        count = 0
        if item == "":  # change later
            category_list.append("")
        else:
            for category, limits in survey_scoring[survey][
                "category"
            ].items():  # appending too many times here
                if item >= limits[0] and item <= limits[1]:
                    category_list.append(category)
                    count += 1
    average_header = f"{prefix}_average_score"
    df[average_header] = average_list
    total_header = f"{prefix}_total_score"
    df[total_header] = total_list
    category_header = f"{prefix}_cat"
    df[category_header] = category_list
    return df


def score_eq5d_survey(
    survey: str,
    survey_question_list: list,
    prefix: str,
    df: pd.DataFrame,
    survey_scoring: dict,
) -> pd.DataFrame:
    """Calculates average, total, and category scores with special logic for EQ5D survey

    Arguments:
        survey: name of the survey form config
        survey_question_list: list of data frame columns that make up the survey questions
        prefix: prefix of df columns that identify this survey's questions
        df: survey data frame
        survey_scoring: dictionary with survey scoring config

    Returns:
        d: final scored dataframe
    """
    scoring_dict = {
        "qq_eq5d_mobility": {
            "1": 0,
            "2": 0.096,
            "3": 0.122,
            "4": 0.237,
            "5": 0.322,
        },
        "qq_eq5d_selfcare": {
            "1": 0,
            "2": 0.089,
            "3": 0.107,
            "4": 0.220,
            "5": 0.261,
        },
        "qq_eq5d_usual_activities": {
            "1": 0,
            "2": 0.068,
            "3": 0.101,
            "4": 0.255,
            "5": 0.255,
        },
        "qq_eq5d_pain_discomfort": {
            "1": 0,
            "2": 0.060,
            "3": 0.098,
            "4": 0.318,
            "5": 0.414,
        },
        "qq_eq5d_anxiety_depression": {
            "1": 0,
            "2": 0.057,
            "3": 0.123,
            "4": 0.299,
            "5": 0.321,
        },
    }
    index_score_list = []
    for _, row in df.iterrows():
        value_list = []
        for question, _ in scoring_dict.items():
            value_list.append(scoring_dict[question][row[question]])
        index_score_list.append(1 - sum(value_list))
    df["qq_eq5d_index_score"] = index_score_list
    return df
