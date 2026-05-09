"""
News Article Scraper Module.

Scrapes road-safety-related articles from Indian news sources
(The Hindu, TOI, Deccan Chronicle, etc.) focused on Hyderabad.
Uses newspaper3k for article extraction and BeautifulSoup for link discovery.
"""

import time
import random
import logging
from urllib.parse import urlparse
from typing import Optional

import requests
from bs4 import BeautifulSoup
from newspaper import Article

from config.settings import (
    NEWS_SOURCES, ROAD_SAFETY_KEYWORDS, HTTP_HEADERS,
    MAX_PAGES_PER_SOURCE, REQUEST_DELAY_MIN, REQUEST_DELAY_MAX,
    TARGET_CITY
)

logger = logging.getLogger(__name__)


class NewsArticleScraper:
    """
    Scrapes news articles from multiple Indian news sources,
    filtering for road safety content related to Hyderabad.
    """

    def __init__(self, sources=None, keywords=None, max_pages=None):
        self.sources = sources or NEWS_SOURCES
        self.keywords = [kw.lower() for kw in (keywords or ROAD_SAFETY_KEYWORDS)]
        self.max_pages = max_pages or MAX_PAGES_PER_SOURCE
        self.headers = HTTP_HEADERS
        self._seen_urls = set()

    def discover_links(self) -> list[dict]:
        """
        Crawl all configured news sources and discover article URLs
        that match road safety keywords.

        Returns:
            List of dicts with 'title' and 'url' keys.
        """
        found_links = []
        for source in self.sources:
            logger.info(f"🔍 Scanning source: {source}")
            try:
                links = self._crawl_source(source)
                found_links.extend(links)
                logger.info(f"   Found {len(links)} potential articles")
            except Exception as e:
                logger.warning(f"   Error scraping {source}: {e}")

        # Deduplicate by URL
        unique = list({v["url"]: v for v in found_links}.values())
        logger.info(f"📊 Total unique articles discovered: {len(unique)}")
        return unique

    def extract_article(self, url: str) -> Optional[dict]:
        """
        Download and parse a single article, extracting structured data.

        Args:
            url: Article URL to process.

        Returns:
            Dict with article data, or None if not relevant/failed.
        """
        try:
            article = Article(url)
            article.download()
            article.parse()

            text = article.text
            if not text or len(text) < 50:
                return None

            # Check keyword relevance
            text_lower = text.lower()
            found_keywords = [kw for kw in self.keywords if kw in text_lower]
            if not found_keywords:
                return None

            return {
                "title": article.title or "Untitled",
                "text": text,
                "date": (
                    article.publish_date.strftime("%Y-%m-%d")
                    if article.publish_date
                    else "Unknown"
                ),
                "source": urlparse(url).netloc,
                "url": url,
                "authors": ", ".join(article.authors) if article.authors else "Unknown",
                "keywords_found": found_keywords,
            }
        except Exception as e:
            logger.debug(f"Failed to process {url}: {e}")
            return None

    def scrape_all(self, progress_callback=None) -> list[dict]:
        """
        Full scraping pipeline: discover links → extract articles.

        Args:
            progress_callback: Optional callable(current, total, article_data)

        Returns:
            List of extracted article dicts.
        """
        articles_meta = self.discover_links()
        results = []

        for i, meta in enumerate(articles_meta):
            url = meta["url"]
            if url in self._seen_urls:
                continue
            self._seen_urls.add(url)

            logger.info(f"📰 ({i+1}/{len(articles_meta)}) Processing: {url}")
            data = self.extract_article(url)

            if data:
                results.append(data)
                if progress_callback:
                    progress_callback(i + 1, len(articles_meta), data)

            # Polite delay
            time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))

        logger.info(f"✅ Scraping complete. {len(results)} relevant articles extracted.")
        return results

    # ── Private helpers ──────────────────────────────────────────────────

    def _crawl_source(self, source: str) -> list[dict]:
        """Crawl paginated source for article links."""
        links = []
        for page in range(1, self.max_pages + 1):
            page_url = source if page == 1 else f"{source.rstrip('/')}/page-{page}/"
            try:
                resp = requests.get(page_url, headers=self.headers, timeout=15)
                if resp.status_code != 200:
                    break
                soup = BeautifulSoup(resp.text, "html.parser")
                page_links = self._extract_links(soup, source)
                if not page_links:
                    break  # No more relevant links on this page
                links.extend(page_links)
                time.sleep(random.uniform(0.5, 1.5))
            except requests.RequestException as e:
                logger.debug(f"Page {page} failed for {source}: {e}")
                break
        return links

    def _extract_links(self, soup: BeautifulSoup, source: str) -> list[dict]:
        """Extract and filter article links from a page."""
        links = []
        base = urlparse(source)

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if not href.startswith("http"):
                href = f"{base.scheme}://{base.netloc}{href}"

            href_lower = href.lower()
            anchor_text = a_tag.get_text(strip=True).lower()

            # Must mention target city
            city_lower = TARGET_CITY.lower()
            if city_lower not in href_lower and city_lower not in anchor_text:
                continue

            # Must match at least one keyword
            if not any(kw in href_lower or kw in anchor_text for kw in self.keywords):
                continue

            # Skip index/category pages
            skip_suffixes = [
                f"/{city_lower}", f"/city/{city_lower}",
                f"/tag/{city_lower}", f"/category/{city_lower}"
            ]
            if any(href_lower.rstrip("/").endswith(s) for s in skip_suffixes):
                continue

            links.append({"title": a_tag.get_text(strip=True), "url": href})

        return links
