"""
Data Storage Module.
Handles saving/loading of scraped and analyzed data in CSV and JSON formats.
"""

import os
import csv
import json
import logging
from datetime import datetime
from config.settings import OUTPUT_DIR

logger = logging.getLogger(__name__)


class DataStorage:
    """Manages reading and writing of analysis data."""

    CSV_COLUMNS = [
        "title", "date", "source", "url", "authors",
        "keywords_found", "locations", "latitude", "longitude",
        "sentiment_compound", "sentiment_label",
        "severity_level", "severity_confidence", "casualty_count",
        "cleaned_text",
    ]

    def __init__(self, output_dir=None):
        self.output_dir = output_dir or OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    def save_csv(self, records, filename=None):
        """Save records to CSV."""
        if not filename:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"road_safety_analysis_{ts}.csv"

        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.CSV_COLUMNS, extrasaction="ignore")
            writer.writeheader()
            for record in records:
                # Flatten list fields
                row = dict(record)
                for key in ("keywords_found", "locations"):
                    if isinstance(row.get(key), list):
                        row[key] = "; ".join(str(x) for x in row[key])
                writer.writerow(row)

        logger.info(f"💾 CSV saved: {filepath} ({len(records)} records)")
        return filepath

    def save_json(self, records, filename=None):
        """Save records to JSON."""
        if not filename:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"road_safety_analysis_{ts}.json"

        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"💾 JSON saved: {filepath} ({len(records)} records)")
        return filepath

    def save_summary(self, summary, filename=None):
        """Save analysis summary report."""
        if not filename:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_summary_{ts}.json"

        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"📊 Summary saved: {filepath}")
        return filepath

    def load_csv(self, filepath):
        """Load records from CSV file."""
        records = []
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(dict(row))
        return records

    def load_json(self, filepath):
        """Load records from JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
