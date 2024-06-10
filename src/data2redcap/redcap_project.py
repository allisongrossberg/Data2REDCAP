import logging
import os
import json

from redcap import Project

import requests


logger = logging.getLogger(__name__)

def redcap_import(api_url: str, api_key: str, records: list[dict]) -> None:
    records = json.dumps(records)
    data = {"token": api_key, "content": "record", "format": "json", "data": records}
    response = requests.post(api_url, data=data)
    print(response.json())
    return response

# def redcap_import(api_url: str, api_key: str, records: list[dict]) -> None:
    # """Connects to REDCap API Project and uploads data.
    
    # Arguments:
    #     api_url: URL of REDCap API.
    #     api_key: API key.
    #     records: List of records to upload.

    # """
    # project = Project(api_url, api_key)
    # project.import_records(records, return_format_type="json")

# api_url = "https://redcap.du.edu/api/"
# api_key = os.environ.get("REDCAP_AUTH_TOKEN")
# project = Project(api_url, api_key)
# #creat list of numbers 1-125 as strings
# record_numbers = [str(i) for i in range(1, 126)]
# data = project.delete_records(record_numbers)

