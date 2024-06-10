import os

import logging
import json

from typer import Argument, Typer

from data2redcap.transform.transform import transform_all_data_sources
from data2redcap.utils import create_final_redcap_format, export_file, load_config
from data2redcap.redcap_project import redcap_import

logger = logging.getLogger(__name__)


def main(config_path: str) -> None:
    """Main function for data2redcap. Loads config, transforms all data, and creates export.

    Arguments:
        config_path: String path to configuration file.
    """
    logger.info("Starting data processing.")
    # loads config into dictionary
    process_config, source_config = load_config(config_path=config_path)
    logger.info("Loaded config.")
    # performs all data transformations
    df_dict = transform_all_data_sources(
        process_config=process_config, source_config=source_config
    )
    logger.info("Transformed all data sources.")
    # create final redap format df
    upload_records = create_final_redcap_format(
        df_dict=df_dict, process_config=process_config, event=process_config["event"]
    )
    # export dict to json
    # with open("records.json", "w") as outfile:
    #     json.dump(upload_records, outfile)
    logger.info("Created final redcap format.")
    # Upload to REDCAP
    logger.info("Uploading data to REDCAP.")
    response = redcap_import(
        api_url=process_config["redcap_api"]["url"],
        api_key=os.environ.get(process_config["redcap_api"]["key"]),
        records=upload_records,
    )
    print(response)
    logger.info("Data successfully uploaded to REDCap")


app = Typer()


config_path_arg = Argument(..., help="Path to configuration file for data processing")


@app.command()
def run(
    config_path: str = config_path_arg,
):
    main(config_path=config_path)


if __name__ == "__main__":
    app()
