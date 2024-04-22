import logging

import fnmatch

import pandas as pd


logger = logging.getLogger(__name__)


def _set_tbi_status(df: pd.DataFrame) -> pd.DataFrame:
    """Generates tbi_status column.

    Args:
        df: Data frame with tbi history columns.

    Returns:
        pd.DataFrame: Data frame with qq_mtbi_status column.
    """
    tbi_history_list = []
    for val in df["qq_tbi_history___10"]:
        if val == "1":
            tbi_history_list.append("1")  # mTBI (-)
        else:
            tbi_history_list.append("2")  # mTBI (+)
    df["qq_mtbi_status"] = tbi_history_list
    return df


def _set_covid_status(df: pd.DataFrame) -> pd.DataFrame:
    """Generates covid19_status column.

    Arguments:
        df: Data frame with covid-19 history columns.

    Returns:
        pd.DataFrame: Data frame with qq_covid19_status column.
    """
    covid_history_header_list = fnmatch.filter(
        list(df.columns), "qq_covid_?_test_results"
    ) + fnmatch.filter(list(df.columns), "qq_covid_??_test_results")
    covid_history_list = []
    for _, row in df.iterrows():
        code = "1"  # COVID (-) default
        for header in covid_history_header_list:
            if row[header] == "1":
                code = "2"  # COVID (+)
        covid_history_list.append(code)
    df["qq_covid19_status"] = covid_history_list
    return df


def _set_suspected_covid19_status(df: pd.DataFrame) -> pd.DataFrame:
    """Generates suspected_covid19 column.

    Arguments:
        df: Data frame with covid-19 history columns.

    Returns:
        pd.DataFrame: Data frame with qq_suspected_covid19 column.
    """
    suspected_covid_list = []
    for val in df["qq_covid_number"]:
        if val == "11":
            suspected_covid_list.append("2")  # no
        else:
            suspected_covid_list.append("1")  # yes
    df["qq_suspected_covid19"] = suspected_covid_list
    return df


def _set_study_group(df: pd.DataFrame) -> pd.DataFrame:
    """Generates group column.

    Arguments:
        df: Data frame with tbi and covid-19 status columns.

    Returns:
        pd.DataFrame: Data frame with qq_group column.
    """
    group_list = []
    for _, row in df.iterrows():
        if row["qq_mtbi_status"] == "2":  # mTBI (+)
            if row["qq_covid19_status"] == "2":  # COVID (+)
                group_list.append("1")  # mTBI (+), COVID (+)
            else:  # COVID (-)
                group_list.append("4")  # mTBI (+), COVID (-)
        else:  # mTBI (-)
            if row["qq_covid19_status"] == "2":  # COVID (+)
                group_list.append("3")  # mTBI (-), COVID (+)
            else:  # COVID (-)
                group_list.append("2")  # mTBI (-), COVID (-)
    df["qq_group"] = group_list
    return df


def _set_covid_symptom_status(df: pd.DataFrame) -> pd.DataFrame:
    """Generates qq_covid19_symptom_status column.

    Arguments:
        df: Data frame with covid-19 symptom columns.

    Returns:
        pd.DataFrame: Data frame with qq_covid19_symptom_status column.
    """
    covid_symptom_header_list = fnmatch.filter(
        list(df.columns), "qq_covid_?_duration_*"
    ) + fnmatch.filter(list(df.columns), "qq_covid_??_duration_*")
    covid_symptom_status_list = []
    for _, row in df.iterrows():
        symptom_dict = {"chronic": 0, "acute": 0}
        for header in covid_symptom_header_list:
            if row[header] in ["4", "5", "6"]:
                symptom_dict["chronic"] += 1
            elif row[header] in ["1", "2", "3"]:
                symptom_dict["acute"] += 1
        if symptom_dict["chronic"] > 0:
            covid_symptom_status_list.append("2")  # Chronic Symptoms
        elif symptom_dict["chronic"] == 0 and symptom_dict["acute"] > 0:
            covid_symptom_status_list.append("3")  # Acute Symptoms
        else:
            covid_symptom_status_list.append("1")  # No Symptoms
    df["qq_covid19_symptom_status"] = covid_symptom_status_list
    return df


def _set_tbi_symptom_status(df: pd.DataFrame) -> pd.DataFrame:
    """Generates qq_tbi_symptom_status column.

    Arguments:
        df: Data frame with tbi symptom columns.

    Returns:
        pd.DataFrame: Data frame with qq_tbi_symptom_status column.
    """
    tbi_symptom_header_list = fnmatch.filter(
        list(df.columns), "qq_tbi_?_duration_*"
    ) + fnmatch.filter(list(df.columns), "qq_tbi_??_duration_*")
    tbi_symptom_status_list = []
    for _, row in df.iterrows():
        symptom_dict = {"chronic": 0, "acute": 0}
        for header in tbi_symptom_header_list:
            if row[header] in ["4", "5", "6"]:
                symptom_dict["chronic"] += 1
            elif row[header] in ["1", "2", "3"]:
                symptom_dict["acute"] += 1
        if symptom_dict["chronic"] > 0:
            tbi_symptom_status_list.append("2")  # Chronic Symptoms
        elif symptom_dict["chronic"] == 0 and symptom_dict["acute"] > 0:
            tbi_symptom_status_list.append("3")  # Acute Symptoms
        else:
            tbi_symptom_status_list.append("1")  # No Symptoms
    df["qq_mtbi_symptom_status"] = tbi_symptom_status_list
    return df


def set_status_and_group(df: pd.DataFrame, grouping: bool) -> pd.DataFrame:
    """Adds grouping and status columns to data frame. If grouping is not necessary, returns unchanged df.

    Arguments:
        df: Data source data frame.
        grouping: Boolean indicating if grouping is necessary.

    Returns:
        df: Data frame with grouping and status columns.
    """
    if not grouping:
        logger.info("No grouping variables provided in data source config")
        return df
    tbi_status_df = _set_tbi_status(df=df)
    covid_status_df = _set_covid_status(df=tbi_status_df)
    suspected_covid_df = _set_suspected_covid19_status(df=covid_status_df)
    grouped_df = _set_study_group(df=suspected_covid_df)
    covid_symptom_df = _set_covid_symptom_status(df=grouped_df)
    final_df = _set_tbi_symptom_status(df=covid_symptom_df)
    logger.info("Grouping logic successfully applied to data source")
    return final_df
