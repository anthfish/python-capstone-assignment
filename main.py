import argparse
import logging
import os
import csv
import requests
import json
import zipfile
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
	filename="logs/errors.log",
	level=logging.INFO,
	format="%(asctime)s [%(levelname)s] %(message)s",
	datefmt="%Y-%m-%d %H:%M:%S"
)

def load_critical_logs(filepath):
	critical_rows = []

	try:
		with open(filepath, newline="") as f:
			reader = csv.DictReader(f)
			for row in reader:
				if row ["level"] == "CRITICAL":
					critical_rows.append(row)

		logging.info(f"Loaded {len(critical_rows)} CRITICAL entries from {filepath}")
		print(f"[INFO] Found {len(critical_rows)} CRITICAL entries")

	except FileNotFoundError:
		logging.error(f"Log file not found: {filepath}")
		print(f"[ERROR] File not found: {filepath}")
		raise

	return critical_rows

def get_weather(location):
	url = "http://api.weatherapi.com/v1/current.json"

	try:
		response = requests.get(url, params={"key": WEATHER_API_KEY, "q": location})
		response.raise_for_status()
		data = response.json()

		temp = data["current"]["temp_c"]
		condition = data["current"]["condition"]["text"]

		logging.info(f"Weather fetched for {location}: {temp}C, {condition}")
		print(f"[INFO] Weather for {location}: {temp}C, {condition}")

		return {"temp_c": temp, "condition": condition}

	except requests.exceptions.HTTPError as e:
		logging.error(f"HTTP error fetching weather: {e}")
		print(f"[ERROR] HTTP error: {e}")
	except requests.exceptions.ConnectionError:
		logging.error("Connection error - check network or API URL")
		print("[ERROR] Connection error")
	except ValueError:
		logging.error("Invalid JSON returned from weather API")
		print("[ERROR] Invalid JSON from API")

	return {"temp_c": "N/A", "condition": "N/A"}

def enrich_and_export(critical_logs):
	timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	csv_filename = f"report_{timestamp}.csv"
	json_filename = f"report_{timestamp}.json"

	enriched = []

	for row in critical_logs:
		weather = get_weather(row["location"])
		row["temp_c"] = weather["temp_c"]
		row["condition"] = weather["condition"]
		enriched.append(row)

	try:
		with open(csv_filename, "w", newline="") as f:
			fieldnames = list(enriched[0].keys())
			writer = csv.DictWriter(f, fieldnames=fieldnames)
			writer.writeheader()
			writer.writerows(enriched)
		logging.info(f"CSV export written: {csv_filename}")
		print(f"[INFO] CSV written: {csv_filename}")
	except Exception as e:
		logging.error(f"Failed to write CSV: {e}")
		print(f"[ERROR] CSV write failed: {e}")

	try:
		with open(json_filename, "w") as f:
			json.dump(enriched, f, indent=4)
		logging.info(f"JSON export written: {json_filename}")
		print(f"[INFO] JSON written: {json_filename}")
	except Exception as e:
		logging.error(f"Failed to write JSON: {e}")
		print(f"[ERROR] JSON write failed: {e}")

	return csv_filename, json_filename

def zip_exports(csv_file, json_file):
	timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	zip_filename = f"output_{timestamp}.zip"

	try:
		with zipfile.ZipFile(zip_filename, "w") as zipf:
			zipf.write(csv_file)
			zipf.write(json_file)
		logging.info(f"Zip created: {zip_filename}")
		print(f"[INFO] Zip created: {zip_filename}")
	except Exception as e:
		logging.error(f"Failed to create zip: {e}")
		print(f"[ERROR] Zip failed: {e}")

	return zip_filename

def main():
	parser = argparse.ArgumentParser(description="Log + Weather Enrichment Tool")
	parser.add_argument("logfile", help="Path to the input CSV log file")
	args = parser.parse_args()

	logging.info("Script started")
	print(f"[INFO] Script started")

	critical_logs = load_critical_logs(args.logfile)

	csv_file, json_file = enrich_and_export(critical_logs)

	zip_file = zip_exports(csv_file, json_file)

	if critical_logs:
		test_location = critical_logs[0]["location"]
		get_weather(test_location)

	logging.info("Script finished")
	print("[INFO] Script finished")

if __name__ == "__main__":
	main()
