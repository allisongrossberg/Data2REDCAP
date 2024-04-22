import logging

from typer import Argument, Typer

from data2redcap.transform.transform import transform_all_data_sources
from data2redcap.utils import create_final_redcap_format, export_file, load_config

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
    export_df = create_final_redcap_format(
        df_dict=df_dict, process_config=process_config
    )
    logger.info("Created final redcap format.")
    # export with today's date
    export_file(export_df, process_config["file_structure"])
    logger.info("Exported final redcap import.")


app = Typer()


config_path_arg = Argument(..., help="Path to configuration file for data processing")


@app.command()
def run(
    config_path: str = config_path_arg,
):
    main(config_path=config_path)


if __name__ == "__main__":
    app()
