import logging

import pandas as pd

from data2redcap.utils import (
    load_data_file,
    file_backup,
    create_final_data_dictionary,
    load_redcap_headers,
)
from data2redcap.transform.survey import calculate_special_survey_scoring
from data2redcap.transform.grouping import set_status_and_group

logger = logging.getLogger(__name__)


def transform_all_data_sources(process_config: dict, source_config: dict) -> dict:
    """Transforms all data sources.

    Arguments:
        process_config: Dictionary containing configuration for overall data processing.
        source_config: Dictionary containing configuration for all individual data sources.

    Returns:
        df_dict: Dictionary of transformed data source data frames.
    """
    df_dict = {}
    for data_source, config in source_config.items():
        # ignore if no file_path
        if not config["file_name"]:
            logger.info(f"No file path in config for {data_source}")
            continue
        # load file and move to back up location
        source_df = load_data_file(
            config["file_name"], process_config["file_structure"], config["type"]
        )
        transformed_df = transform_data_source(config=config, source_df=source_df)
        df_dict.update({data_source: transformed_df})
        file_backup(config["file_name"], process_config["file_structure"])
    return df_dict


def transform_data_source(config: dict, source_df: pd.DataFrame) -> pd.DataFrame:
    """Transforms data source data frame.

    Arguments:
        config: Dictionary containing configuration for data source.
        source_df: Data source data frame.

    Returns:
        transformed_df: Transformed data source data frame.
    """
    if config.get("clean"):  # for data that does not need transformation
        return source_df
    # expand data_dict if need be
    data_dict = create_final_data_dictionary(config)
    # translate to redcap headers
    translated_df = load_redcap_headers(source_df, data_dict)
    # survey scoring
    if config["config"].get("survey_scoring"):
        translated_df = calculate_special_survey_scoring(
            translated_df, config["config"]["survey_scoring"]
        )
        logger.info("surveys scored")
    # create grouping/status columns for year 1 q
    grouped_df = set_status_and_group(translated_df, config["config"].get("grouping"))
    # drop not needed columns
    if config["config"].get("drop_cols"):
        grouped_df = grouped_df.drop(columns=config["config"].get("drop_cols"))
    # append df to list
    return grouped_df
