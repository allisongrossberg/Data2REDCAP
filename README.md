# Data2REDCAP

## Setup

### Prerequisites

The first prerequisite is that you have Python 3 installed on your system. If you do not, you can install it [here](https://www.python.org/downloads/). The second is that you have git installed, if you do not you can find instructions for installing it for your system [here](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).

###### Check that you have Python installed properly

To check that you have python installed properly, open your command prompt and simply run "python" (in some systems, you may need to use python3 instead)

If you do this and the python terminal starts (you should see some information printed followed by a line with ">>>" on it), then you are all set with python.

###### Check that you have Git installed properly

To check that you have git installed properly, open your command prompt and enter the following:

```
git --version
```

If the terminal returns a verison number, your installation worked.

###### Configure git in your terminal

The final thing that you will need to do is to configure your github account in git in your terminal. Instructions for doing this can be found [here](https://git-scm.com/docs/git-config).

### Clone the git repository

###### Copy the .git link

Navigate to the repository page on Github, click Code, and click the copy button next to the HTTPS url ending in ".git".

###### Clone the repo to your selected directory

After copying the url, open your command prompt.

Using the "cd" command, navigate to the location on your computer that you wish to host the script.

> This works best if you select a location that is on a physical hard drive, such as your C or D drive. Cloud locations (OneDrive, or iCloud in the directory path) tend to be less stable.

Once you have picked a location, enter the following into your command prompt:

```
git clone <copied_url>
```

If this step is successful, you should now see a folder called "Data2REDCAP" in the location that you selected and you are ready to use the script!

## Using the script

### Set Up Virtual Environment

Before the tool will work, we need to make sure that we are running it in a version of Python has all of the necessary packages and modules. To do this, we will use `pipenv`. If you have not already installed `pipenv` you can do so with a simple `pip install pipenv` command. Once installed, you can run `pipenv install` from within the `Data2REDCAP` directory and finally, `pipenv shell` to activate the virtual environment.

### Set Up

#### Folder Structure

`Data2REDCAP` depends on a specific folder structure to work properly. To start, you need to create a folder called `files` somewhere on your machine. It is recommended that you place this folder within the `Data2REDCAP` repository itself (This folder is included in the `gitignore` file so any data you add to it will never be committed to the repository on GitHub). Within the `files` folder, you also need to include the following subfolders:
1. `data_files`: This is where the input data files will go.
1. `data_backup`: Input files will be moved here after they are processed.
1. `redcap_imports`: This is where the final output file will be exported.

You should also include your data key file in the `files` folder on the top level.

#### Configuration

`Data2REDCAP` requires a configuration file in order to determine what processing needs to happen for specific data sources.

The configuration file is a JSON file with two main sections, `process_config` and `data_sources`. 

`process_config` includes general information that the tool needs:
1. `file_parent_folder_path`: The path to the `files` folder on your machine.
1. `data_sources_folder`: The name of the folder that contains the data source files within the `files` folder.
1. `data_backup_folder`: The name of the folder that contains the data backup files within the `files` folder.
1. `final_export_location`: The name of the folder that will contain the final export files within the `files` folder.
1. `data_key_path`: The path to the data key file within the `files` folder.

`data_sources` includes information about the data sources that the tool needs to process. Each data source has its own section within `data_sources`. Each section must include:
1. `type`: The type of data source, either "Qualtrics" or "Spreadsheet".
1. `file_name`: The name of the data source file. If this is left blank, the data source will not be processed. If it is not blank, but the file is not in the expected location (`data_files`) or the name is incorrect, this will cause an error. 
1. `union`: If this is a consent form, put "consent" here so that the tool combines the records. Otherwise, put null here.
1. `config`: The configuration for the data source.
    - `clean`: If your data source is already clean and in the correct format (no transformation needed)
    - `data_dictionary`: If your dataset needs column headers to be translated during transformation
    - `looping_questions`: If your data source has any looping fields (surveys)
    - `survey_scoring`: If your data source has any survey scoring
    - `grouping`: If your data source uses custom grouping logic

See the config_example.json file for an example.

### Running the script

Once your configuration is complete and your data files are all in the expected location, you are ready to run the pipeline.

To do so, open your command prompt, navigate to the `Data2REDCAP` directory using the "cd" command, and enter the following:

```
d2r path/to/config.json
```

The script will then process each data source in the `data_sources` section of the configuration file.

If the script is successful, your export file will disappear from the `redcap_imports` folder.

#### Data Sources

In order for this to work properly, there are a few more things to keep in mind:
1. Ensure that each data source has a column `participant_id` in it containing unique identifiers for each participant.
1. Ensure that year 1 questionnaires have "QY1" in the file name.
