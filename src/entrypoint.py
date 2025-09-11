# entrypoint.py
import os
import time
import subprocess
import sys
import logging
import json

INTERVAL = int(os.environ.get("SCAN_INTERVAL_SECONDS", 3600))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def run_scraper():
    logging.info("Running scraper...")
    result = subprocess.run(
        [sys.executable, "/app/scrape.py"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        logging.error(f"Scraper failed with exit code {result.returncode}")
        logging.error(result.stderr)
        return

    logging.info("Scraper finished successfully.")

    # Attempt to parse summary from scrape output if saved as JSON
    snapshot_file = "/app/snapshot.json"
    if os.path.exists(snapshot_file):
        with open(snapshot_file, "r", encoding="utf-8") as f:
            all_files = json.load(f)
        num_files = len(all_files)
        logging.info(f"Total files processed: {num_files}")
    else:
        logging.warning(f"{snapshot_file} not found, cannot summarize files.")

def main():
    logging.info(f"Starting loop with interval {INTERVAL} seconds.")
    try:
        while True:
            run_scraper()
            logging.info(f"Sleeping for {INTERVAL} seconds...")
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        logging.info("Shutting down gracefully.")

if __name__ == "__main__":
    main()
