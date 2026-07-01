Log + Weather Enrichment Tool
==============================
Author: Anthony Fisher

DESCRIPTION
-----------
A monolithic Python automation script that reads a CSV log file, filters for
CRITICAL entries, enriches them with live weather data from weatherapi.com,
and exports the results to both CSV and JSON formats, packaged into a zip archive.

REQUIREMENTS
------------
Python 3.x
pip install -r requirements.txt

SETUP
-----
1. Create a .env file in the project root with your API key:
   WEATHER_API_KEY=your_key_here

2. Prepare an input CSV log file with columns:
   timestamp, level, message, location

USAGE
-----
python3 main.py logs.csv

OUTPUT
------
- report_<timestamp>.csv
- report_<timestamp>.json
- output_<timestamp>.zip
- logs/errors.log
