import pandas as pd
import shutil
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def load_config(config_path: str) -> tuple[dict, dict]:
    """Loads config file into dictionaries.

    Arguments:
        config_path: String path to configuration file.

    Returns:
        process_config: Dictionary containing configuration for overall data processing.
        source_config: Dictionary containing configuration for all individual data sources.
    """
    with open(config_path) as file:
        config = json.load(file)
    process_config = config["process_config"]
    source_config = config["data_sources"]
    return process_config, source_config


def _create_file_path(*args: list[str]) -> str:
    """Combines all arguments into a single path string.

    Arguments:
        args: List of strings.

    Returns:
        str: Path made of joined string arguments.
    """
    return "/".join(args)


def file_backup(file_name: str, file_structure: dict) -> None:
    """Moves data file to backup folder

    Arguments:
        file_name: Name of data file.
        file_structure: Dictionary containing configuration for file locations.
    """
    file_path = _create_file_path(
        file_structure["file_parent_folder_path"],
        file_structure["data_sources_folder"],
        file_name,
    )
    backup_path = _create_file_path(
        file_structure["file_parent_folder_path"],
        file_structure["data_backup_folder"],
        file_name,
    )
    shutil.move(file_path, backup_path)


def _clean_qualtrics_data(df: pd.DataFrame) -> pd.DataFrame:
    """Performs cleaning of qualtrics data.

    Args:
        df: Qualtrics data frame.

    Returns:
        clean_df: Cleaned qualtrics data frame.
    """
    df = df.drop([0, 1]).reset_index()
    clean_df = df[df["Progress"] == "100"]
    return clean_df


def load_data_file(
    file_name: str, file_structure: dict, file_type: str
) -> pd.DataFrame:
    """Loads data files into data frame for processing

    Arguments:
        file_name: Name of data file.
        file_structure: Dictionary containing configuration for file locations.
        file_type: Type of data source.

    Returns:
        df: Data frame
    """

    file_path = _create_file_path(
        file_structure["file_parent_folder_path"],
        file_structure["data_sources_folder"],
        file_name,
    )
    # read file from path
    # TODO better file extension handling
    if file_name.endswith(".csv"):
        # TODO pull out into config
        if "QY1" in file_name:
            df = pd.read_csv(file_path, dtype=str)
        else:
            df = pd.read_csv(file_path)

    elif file_name.endswith(".xlsx"):
        df = pd.read_excel(file_path)
    else:
        raise ImportError("File type not supported. Must be either `.csv` or `.xlsx`")
    if file_type == "Qualtrics":
        df = _clean_qualtrics_data(df)
    logger.info(f"{file_name} loaded")
    return df


def create_final_data_dictionary(config: dict) -> dict:
    """Generates final data dictionary with looping questions.

    Arguments:
        config: Dictionary containing configuration for data sources.

    Returns:
        data_dict: Final data dictionary for data sources.
    """
    data_dict = config["config"].get("data_dictionary")
    if data_dict is None:
        logger.info("No data dictionary provided in data source config")
        return data_dict
    if (
        config["config"].get("looping_questions") is None
        or len(config["config"].get("looping_questions")) == 0
    ):
        logger.info("No looping questions present in data source config")
        return data_dict
    else:
        looping_dict = config["config"].get("looping_questions")
        new_dict = {}
        for prefix, number in looping_dict.items():
            for k, v in data_dict.items():
                if k.startswith("1_") and (
                    "vaccine" not in v and "vaccination" not in v
                ):
                    new_dict.update({k: v})
                    if v.startswith(prefix):
                        for i in range(number):
                            if i != 0:
                                key = str(i + 1) + "_" + k.split("_", 1)[1]
                                value = (
                                    v.split("1", 1)[0] + str(i + 1) + v.split("1", 1)[1]
                                )
                                new_dict.update({key: value})
                else:
                    new_dict.update({k: v})
        logger.info("data dictionary successfully expanded for looping questions")
        return new_dict


def load_redcap_headers(df: pd.DataFrame, data_dict: dict) -> pd.DataFrame:
    """Renames data frame column headers to redcap headers. Drops not needed columns.

    Arguments:
        df: Data source data frame.
        data_dict: Data dictionary for data source.

    Returns:
        df_final: Final data frame with redcap headers.
    """
    if data_dict is None:
        logger.info("No data dictionary provided in data source config")
        return df
    for header in list(df.columns):
        if header not in data_dict:
            df.drop(header, axis=1, inplace=True)
    df_final = df.rename(columns=data_dict)
    logger.info("Column headers successfully translated")
    return df_final


def join_with_data_key(data_key_path: str, df_list: list[pd.DataFrame]) -> pd.DataFrame:
    """Joins all data sources on data key.

    Arguments:
        data_key_path: Path to data key.
        df_list: List of data source data frames.

    Returns:
        data_key_df: Data frame with all data sources merged with data key.
    """
    data_key_df = pd.read_excel(data_key_path)
    for df in df_list:
        # strip trailing and leading spaces from participant_id
        df["participant_id"] = df["participant_id"].str.strip()
        data_key_df = data_key_df.merge(df, on="participant_id", how="left")
    logger.info("Data key successfully added to merged data")
    return data_key_df


def create_final_redcap_format(df_dict: dict, process_config: dict) -> pd.DataFrame:
    """Creates final redcap data frame.

    Arguments:
        df_dict: Dictionary of data source data frames.
        process_config: Dictionary containing configuration for overall data processing.

    Returns:
        export_df: Final redcap data frame.
    """
    # create final list of dataframe to merge
    final_df_list = create_final_df_list(df_dict=df_dict)
    # join dfs
    wide_joined_df = join_with_data_key(
        process_config["file_structure"]["data_key_path"], final_df_list
    )
    logger.info("All data sources successfully merged with data key")
    # add column where every value is "Record" in the first column slot
    wide_joined_df[" "] = "Record"
    # transpose with Record being at the to
    export_df = wide_joined_df.set_index(" ").T
    return export_df


def create_final_df_list(df_dict: dict) -> list[pd.DataFrame]:
    """Creates final list of data frames before merging.

    Arguments:
        df_dict: Dictionary of data source data frames.

    Returns:
        final_df_list: Final list of data frames.
    """
    consent_df_list = []
    questionnaire_df_list = []
    final_df_list = []
    for key, value in df_dict.items():
        if "consent" in key:
            consent_df_list.append(value)
        elif "questionnaire" in key:
            questionnaire_df_list.append(value)
        else:
            final_df_list.append(value)
    if consent_df_list:
        consent_df = pd.concat(consent_df_list)
        final_df_list.append(consent_df)
    if questionnaire_df_list:
        questionnaire_df = pd.concat(questionnaire_df_list)
        final_df_list.append(questionnaire_df)
    return final_df_list


def export_file(df: pd.DataFrame, file_structure: dict) -> None:
    """Exports data frame to csv file.

    Arguments:
        df: Data frame to export.
        file_structure: Dictionary containing configuration for file locations.
    """
    str_dt = datetime.today().strftime("%Y-%m-%d")
    file_path = _create_file_path(
        file_structure["file_parent_folder_path"],
        file_structure["final_export_location"],
        f"redcap_import_{str_dt}.csv",
    )
    df.to_csv(file_path)
    logger.info("Redcap import file successfully exported. Process complete.")
