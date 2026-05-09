"""
Road Safety NLP Analysis System - Main Entry Point

Usage:
    python main.py                  # Full pipeline: scrape → analyze → dashboard
    python main.py --scrape-only    # Only scrape articles
    python main.py --analyze FILE   # Analyze from existing CSV/JSON
    python main.py --demo           # Run with sample data for demonstration
"""

import sys
import os
import argparse
import logging
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import OUTPUT_DIR, TARGET_CITY
from scrapers.news_scraper import NewsArticleScraper
from nlp.preprocessor import TextPreprocessor
from nlp.sentiment import SentimentAnalyzer
from nlp.ner import LocationExtractor
from nlp.classifier import SeverityClassifier
from geo.geocoder import Geocoder
from data.storage import DataStorage
from visualization.dashboard import DashboardGenerator

# ─── Logging Setup ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-7s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def run_full_pipeline(max_pages=5, skip_geocoding=False):
    """Run the complete scraping → NLP → dashboard pipeline."""
    print("\n" + "="*60)
    print("🚦 Road Safety NLP Analysis System")
    print(f"   Target: {TARGET_CITY} | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60 + "\n")

    # ── Step 1: Scrape ──
    print("📡 STEP 1/5: Scraping news articles...")
    scraper = NewsArticleScraper(max_pages=max_pages)
    raw_articles = scraper.scrape_all()
    if not raw_articles:
        logger.warning("No articles found. Try increasing max_pages or check network.")
        return None
    print(f"   ✅ Scraped {len(raw_articles)} relevant articles\n")

    # ── Step 2-5: Analyze ──
    return analyze_articles(raw_articles, skip_geocoding=skip_geocoding)


def analyze_articles(raw_articles, skip_geocoding=False):
    """Run NLP analysis pipeline on a list of articles."""

    # ── Step 2: Preprocess ──
    print("🧹 STEP 2/5: Preprocessing text...")
    preprocessor = TextPreprocessor()
    for article in raw_articles:
        article["cleaned_text"] = preprocessor.clean_for_analysis(article.get("text", ""))
    print(f"   ✅ Preprocessed {len(raw_articles)} articles\n")

    # ── Step 3: NLP Analysis ──
    print("🧠 STEP 3/5: Running NLP analysis...")
    sentiment_analyzer = SentimentAnalyzer()
    location_extractor = LocationExtractor()
    severity_classifier = SeverityClassifier()

    for i, article in enumerate(raw_articles):
        text = article.get("text", "")

        # Sentiment
        sent = sentiment_analyzer.analyze(text)
        article["sentiment_compound"] = sent["compound"]
        article["sentiment_label"] = sent["label"]

        # NER - locations
        locations = location_extractor.extract_locations(text)
        article["locations"] = locations

        # Severity
        sev = severity_classifier.classify(text)
        article["severity_level"] = sev["level"]
        article["severity_confidence"] = sev["confidence"]
        article["casualty_count"] = sev["casualty_count"]
        article["severity_keywords"] = sev["matched_keywords"]

        if (i + 1) % 10 == 0:
            print(f"   Analyzed {i+1}/{len(raw_articles)}...")

    print(f"   ✅ NLP analysis complete\n")

    # ── Step 4: Geocoding ──
    if not skip_geocoding:
        print("📍 STEP 4/5: Geocoding locations...")
        geocoder = Geocoder()
        if geocoder.is_available:
            geocoded = 0
            for article in raw_articles:
                locs = article.get("locations", [])
                if locs:
                    result = geocoder.geocode(locs[0])
                    if result:
                        article["latitude"] = result["lat"]
                        article["longitude"] = result["lon"]
                        geocoded += 1
            print(f"   ✅ Geocoded {geocoded} locations\n")
        else:
            print("   ⚠️  Geocoder unavailable, skipping\n")
    else:
        print("📍 STEP 4/5: Geocoding skipped\n")

    # ── Step 5: Save & Dashboard ──
    print("💾 STEP 5/5: Saving results & generating dashboard...")
    storage = DataStorage()
    csv_path = storage.save_csv(raw_articles)
    json_path = storage.save_json(raw_articles)

    dashboard = DashboardGenerator()
    dash_path = dashboard.generate(raw_articles)

    # Summary
    print("\n" + "="*60)
    print("✅ ANALYSIS COMPLETE!")
    print("="*60)
    print(f"   📊 Articles analyzed : {len(raw_articles)}")
    fatal = sum(1 for a in raw_articles if a.get("severity_level") == "fatal")
    severe = sum(1 for a in raw_articles if a.get("severity_level") == "severe")
    print(f"   💀 Fatal incidents   : {fatal}")
    print(f"   🏥 Severe incidents  : {severe}")
    casualties = sum(a.get("casualty_count", 0) for a in raw_articles)
    print(f"   👥 Total casualties  : {casualties}")
    print(f"\n   📁 CSV  : {csv_path}")
    print(f"   📁 JSON : {json_path}")
    print(f"   📊 Dashboard : {dash_path}")
    print("="*60 + "\n")

    return {"csv": csv_path, "json": json_path, "dashboard": dash_path}


def run_demo():
    """Run with sample data for demonstration."""
    print("\n🎯 Running in DEMO mode with sample data...\n")

    sample_articles = [
        {
            "title": "Two killed in road accident at Madhapur junction",
            "text": "Two people were killed and three injured in a fatal road accident at Madhapur junction in Hyderabad on Monday. A speeding truck rammed into a two-wheeler at the signal, killing both riders on the spot. The injured were rushed to a nearby hospital. Police suspect the truck driver was under the influence of alcohol. Traffic was disrupted for over two hours. Locals demanded better traffic management at the junction. CCTV footage has been obtained by police for investigation.",
            "date": "2025-04-28",
            "source": "thehindu.com",
            "url": "https://example.com/article1",
            "authors": "Staff Reporter",
            "keywords_found": ["killed", "accident", "fatal", "traffic"],
        },
        {
            "title": "Biker injured in hit-and-run near Gachibowli flyover",
            "text": "A bike rider sustained serious injuries after being hit by an unidentified vehicle near the Gachibowli flyover in Hyderabad. The incident occurred around 11 PM on Saturday. The victim, identified as Rajesh Kumar, 28, was admitted to a private hospital with fractures. Police registered a case and are checking CCTV cameras to trace the vehicle. The road stretch is known for speeding vehicles, and locals have repeatedly complained about the lack of speed breakers.",
            "date": "2025-04-25",
            "source": "deccanchronicle.com",
            "url": "https://example.com/article2",
            "authors": "City Correspondent",
            "keywords_found": ["injured", "hit-and-run", "vehicle"],
        },
        {
            "title": "Road safety drive launched at LB Nagar after spike in accidents",
            "text": "Hyderabad traffic police launched a special road safety awareness drive at LB Nagar after a significant increase in accidents over the past three months. Officials said that over 15 accidents, including three fatal ones, were reported in the LB Nagar zone this quarter. The drive includes speed checks, breathalyzer tests, and distribution of helmets to two-wheeler riders. Commissioner urged citizens to follow traffic rules and avoid rash driving. The initiative is part of a larger campaign to reduce road accident deaths in the city.",
            "date": "2025-04-30",
            "source": "timesofindia.indiatimes.com",
            "url": "https://example.com/article3",
            "authors": "TOI Bureau",
            "keywords_found": ["road safety", "accidents", "fatal", "rash driving"],
        },
        {
            "title": "Pedestrian killed by speeding bus near Secunderabad railway station",
            "text": "A 55-year-old pedestrian was killed after being hit by a speeding TSRTC bus near Secunderabad railway station on Wednesday morning. The victim was crossing the road when the bus, reportedly travelling at high speed, struck him. He was declared dead on arrival at Gandhi Hospital. The bus driver has been arrested and the vehicle seized. This is the third fatal accident involving public transport in Hyderabad this month.",
            "date": "2025-05-01",
            "source": "telanganatoday.com",
            "url": "https://example.com/article4",
            "authors": "News Desk",
            "keywords_found": ["killed", "pedestrian", "fatal", "accident"],
        },
        {
            "title": "Minor injuries reported in multi-vehicle pile-up on ORR",
            "text": "A multi-vehicle pile-up on the Outer Ring Road near Shamshabad resulted in minor injuries to five people on Tuesday afternoon. The accident involved four cars and a delivery van. Police said the pile-up was caused by sudden braking due to a pothole on the road. All injured were given first aid at the scene. Traffic was diverted for about an hour. The incident has reignited demands for pothole repairs on the ORR stretch.",
            "date": "2025-04-29",
            "source": "siasat.com",
            "url": "https://example.com/article5",
            "authors": "Staff Writer",
            "keywords_found": ["pile-up", "injured", "pothole", "accident"],
        },
    ]

    return analyze_articles(sample_articles, skip_geocoding=True)


def main():
    parser = argparse.ArgumentParser(
        description="🚦 Road Safety NLP Analysis System — Hyderabad",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    Full pipeline
  python main.py --demo             Demo with sample data
  python main.py --scrape-only      Only scrape articles
  python main.py --max-pages 3      Limit pages per source
  python main.py --no-geocoding     Skip geocoding step
        """
    )
    parser.add_argument("--demo", action="store_true", help="Run demo with sample data")
    parser.add_argument("--scrape-only", action="store_true", help="Only scrape, skip analysis")
    parser.add_argument("--analyze", type=str, help="Analyze existing JSON file")
    parser.add_argument("--max-pages", type=int, default=5, help="Max pages per source")
    parser.add_argument("--no-geocoding", action="store_true", help="Skip geocoding")

    args = parser.parse_args()

    if args.demo:
        run_demo()
    elif args.analyze:
        storage = DataStorage()
        articles = storage.load_json(args.analyze)
        analyze_articles(articles, skip_geocoding=args.no_geocoding)
    elif args.scrape_only:
        scraper = NewsArticleScraper(max_pages=args.max_pages)
        articles = scraper.scrape_all()
        storage = DataStorage()
        storage.save_json(articles)
        print(f"Saved {len(articles)} articles")
    else:
        run_full_pipeline(max_pages=args.max_pages, skip_geocoding=args.no_geocoding)


if __name__ == "__main__":
    main()
