# 🚦 Road Safety NLP Analysis System

**NLP-based classification of road accident severity from social media & news articles — focused on Hyderabad, India.**

> *Design Project (EEE F376) — BITS Pilani, Hyderabad Campus*  
> *Under Prof. Bandhan Majumdar*

## 🏗 Architecture

```
social_media_scrapper/
├── config/settings.py           # Configuration, keywords, sources
├── scrapers/
│   ├── news_scraper.py          # News article scraper (primary)
│   └── twitter_scraper.py       # Twitter/Nitter scraper (secondary)
├── nlp/
│   ├── preprocessor.py          # Text cleaning pipeline
│   ├── sentiment.py             # VADER sentiment analysis
│   ├── ner.py                   # Named entity recognition
│   └── classifier.py            # Accident severity classifier
├── geo/geocoder.py              # Location geocoding
├── data/storage.py              # CSV/JSON data management
├── visualization/dashboard.py   # Interactive HTML dashboard
├── output/                      # Generated results
├── main.py                      # CLI entry point
└── requirements.txt
```

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 2. Run demo (no scraping needed)
python main.py --demo

# 3. Run full pipeline (scrapes live news)
python main.py

# 4. Run with options
python main.py --max-pages 3 --no-geocoding
```

## 📊 Features

| Feature | Description |
|---------|-------------|
| **Multi-source scraping** | 8+ Indian news sources (The Hindu, TOI, DC, etc.) |
| **NLP Pipeline** | Clean → NER → Sentiment → Severity Classification |
| **Severity Classification** | Fatal / Severe / Moderate / Minor / Unclassified |
| **Sentiment Analysis** | VADER compound scores + categorical labels |
| **Location Extraction** | SpaCy NER + Nominatim geocoding |
| **Interactive Dashboard** | HTML report with Chart.js + Leaflet maps |
| **CLI Interface** | Configurable pipeline with --demo, --scrape-only, etc. |

## 📈 Output

The system generates in the `output/` folder:
- **CSV** — Structured data for further analysis in Excel/Pandas
- **JSON** — Full data with nested structures
- **HTML Dashboard** — Interactive charts, map, and data table

## ⚙️ Configuration

Edit `config/settings.py` to customize:
- Target city/region
- Road safety keywords
- Severity indicator keywords
- News sources to scrape
- Scraping delays and limits
