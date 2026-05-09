"""
Central configuration for the Road Safety NLP Analysis System.
All tunable parameters, keywords, sources, and paths are defined here.
"""

import os
from datetime import datetime

# ─── Project Paths ────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── Scraping Configuration ──────────────────────────────────────────────────
TARGET_CITY = "Hyderabad"
TARGET_STATE = "Telangana"
TARGET_COUNTRY = "India"

# Keywords for filtering road-safety-related content
ROAD_SAFETY_KEYWORDS = [
    "accident", "fatal", "injured", "crash", "collision",
    "death", "deceased", "killed", "road safety", "traffic",
    "vehicle", "pedestrian", "hit-and-run", "hit and run",
    "rash driving", "over speeding", "drunk driving",
    "pothole", "road rage", "pile-up", "pileup",
    "two-wheeler", "bike accident", "car accident",
    "lorry", "truck accident", "bus accident",
    "signal jump", "wrong side", "overtaking"
]

# Severity indicator keywords (used for classification)
SEVERITY_KEYWORDS = {
    "fatal": [
        "killed", "death", "deceased", "fatal", "dead", "died",
        "succumbed", "spot dead", "brought dead", "lives lost",
        "perished", "casualty", "casualties", "toll"
    ],
    "severe": [
        "critical", "serious", "grievous", "hospitalised", "hospitalized",
        "icu", "intensive care", "fracture", "head injury", "surgery",
        "amputation", "life-threatening", "multiple injuries",
        "coma", "ventilator", "brain dead"
    ],
    "moderate": [
        "injured", "hurt", "wound", "minor injuries", "bruise",
        "treatment", "first aid", "outpatient", "discharged",
        "bleeding", "sprain", "dislocation"
    ],
    "minor": [
        "damage", "dent", "scratch", "fender bender", "traffic jam",
        "near miss", "narrow escape", "close call", "no casualties",
        "property damage"
    ]
}

# News sources to scrape
NEWS_SOURCES = [
    "https://www.thehindu.com/news/cities/Hyderabad/",
    "https://telanganatoday.com/category/hyderabad",
    "https://www.deccanchronicle.com/nation/current-affairs/hyderabad",
    "https://timesofindia.indiatimes.com/city/hyderabad",
    "https://www.thenewsminute.com/telangana",
    "https://www.siasat.com/news/hyderabad/",
    "https://www.hindustantimes.com/cities/hyderabad-news",
    "https://www.indiaherald.com/Search/en/hyderabad",
]

# Maximum number of pages to crawl per source
MAX_PAGES_PER_SOURCE = 10

# Delay between requests (seconds) to be polite
REQUEST_DELAY_MIN = 1.0
REQUEST_DELAY_MAX = 3.0

# HTTP headers
HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# ─── NLP Configuration ───────────────────────────────────────────────────────
SPACY_MODEL = "en_core_web_sm"

# Locations to exclude from NER (too generic)
EXCLUDED_LOCATIONS = {
    "hyderabad", "telangana", "india", "andhra pradesh",
    "ap", "ts", "indian", "sunday", "monday", "tuesday",
    "wednesday", "thursday", "friday", "saturday"
}

# ─── Output Configuration ────────────────────────────────────────────────────
def get_output_filename(prefix="road_safety_data", ext="csv"):
    """Generate timestamped output filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(OUTPUT_DIR, f"{prefix}_{timestamp}.{ext}")

# ─── Nitter / Twitter Configuration (Secondary) ──────────────────────────────
TWITTER_SEARCH_TERMS = [
    "#RoadSafety Hyderabad",
    "#AccidentHyderabad",
    "#HyderabadTraffic",
    "road accident Hyderabad",
    "crash Hyderabad",
]

TWITTER_MAX_TWEETS = 100
