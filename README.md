# EIC Trace Extraction

Link to GitHub repository: [EIC Trace Extraction](https://github.com/arcamelia/EIC-extraction)

## Purpose Statement
This repository contains a Python script that allows you to prepare chromatogram traces from LC-MS data. Specifically, once you export your MS data as netCDF files from Compass, this script will turn them into CSVs, and extract the EIC information.

## Requirements
- Python is installed on your machine

- The file path to the `Downloads` folder on your machine

    - On Windows, you can get the path of a folder by right clicking on the folder, then clicking 'Copy as path'

    - On a Mac, you can get the path of a folder by right clicking on the folder, then hold down the `option` key while clicking 'Copy "*FOLDER*" as Pathname' (where *FOLDER* is the name of the folder you want the path for)

## Procedure
1. Export MS data as a netCDF file from Compass on the MS data analysis computer (right click on File -> Export -> Export Chromatogram Analysis -> name file with correct prefix -> save as CDF file).

    - __Hint:__ The file name should begin with either of the following prefixes: 'PA66', 'PA6'. This determines which set of m/z values are extracted from the data. If neither of these prefixes are used, the script will not execute successfully.

    - __Hint:__ Repeat this step for every file that you want to analyze (the script allows you to input multiple CDF files at once). 

2. On the GitHub `EIC-extraction` repository webpage, click on the green `<> Code` button, then click 'Download ZIP'.

3. Unzip the downloaded ZIP file. There should now be a folder called `EIC-extraction-main` in your `Downloads` folder.

4. Open up the `EIC-extraction-main` folder. Drop your `.cdf` file(s) from Compass into the `input` folder.

    - __Hint:__ Refer to [Appendix A](#appendix-a-files-in-this-repo) for a description of each of the files in the folder.

5. Open the terminal application on your machine (if you're on Windows, this will be an app called 'Command Prompt'; if you're on a Mac, this will be an app called 'Terminal').

6. Type in the command `cd $DOWNLOADS-FOLDER-PATH$/EIC-extraction-main` (where `$DOWNLOADS-FOLDER-PATH$` is the file path to your `Downloads` folder), then hit enter.

    - __Hint:__ if an error message like `no such file or directory` appears, you might need to use a backslash instead of a forward slash

7. Now you're going to run the Python script. To do this, type in either of the following commands (depending on which version of Python you're running): `python3 extraction.py`, `python extraction.py`, then hit enter.

8. Open the `output` folder and verify that it is populated with your `.csv` files.

## Appendix A: Files in this Repository
### input ### 
Folder containing input data, in the form of `.cdf` files

### output
Folder containing output data, in the form of `.csv` files

### extraction.py
Python script that converts the EIC chromatogram trace data into `.csv` files

### README.md
Contains the documentation and procedural information for users