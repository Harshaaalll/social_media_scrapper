"""
Twitter/Nitter Scraper Module (Secondary Source).

Uses ntscraper to fetch tweets via Nitter instances without needing
Twitter API credentials. This is a supplementary data source.

Note: Nitter instances may be unreliable. This module is designed
to fail gracefully and return empty results if unavailable.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TwitterScraper:
    """
    Scrapes tweets using Nitter (ntscraper) as a secondary data source.
    Falls back gracefully if Nitter instances are unavailable.
    """

    def __init__(self):
        self._scraper = None
        self._available = False
        self._init_scraper()

    def _init_scraper(self):
        """Attempt to initialize ntscraper."""
        try:
            from ntscraper import Nitter
            self._scraper = Nitter(0)
            self._available = True
            logger.info("✅ Nitter scraper initialized successfully")
        except ImportError:
            logger.warning(
                "⚠️  ntscraper not installed. Twitter scraping disabled. "
                "Install with: pip install ntscraper"
            )
        except Exception as e:
            logger.warning(f"⚠️  Nitter initialization failed: {e}")

    @property
    def is_available(self) -> bool:
        """Check if scraper is available."""
        return self._available

    def search_tweets(self, query: str, count: int = 50) -> list[dict]:
        """
        Search tweets by hashtag or keyword.

        Args:
            query: Search term or hashtag (without #).
            count: Number of tweets to retrieve.

        Returns:
            List of tweet dicts with text, date, likes, comments, link.
        """
        if not self._available:
            logger.warning("Twitter scraper unavailable, returning empty results")
            return []

        try:
            tweets = self._scraper.get_tweets(query, mode="hashtag", number=count)
            return self._format_tweets(tweets)
        except Exception as e:
            logger.error(f"Error fetching tweets for '{query}': {e}")
            return []

    def get_user_tweets(self, username: str, count: int = 50) -> list[dict]:
        """
        Get tweets from a specific user.

        Args:
            username: Twitter username (without @).
            count: Number of tweets to retrieve.

        Returns:
            List of tweet dicts.
        """
        if not self._available:
            return []

        try:
            tweets = self._scraper.get_tweets(username, mode="user", number=count)
            return self._format_tweets(tweets)
        except Exception as e:
            logger.error(f"Error fetching tweets for user '{username}': {e}")
            return []

    def get_profile_info(self, username: str) -> Optional[dict]:
        """Get profile information for a Twitter user."""
        if not self._available:
            return None

        try:
            return self._scraper.get_profile_info(username)
        except Exception as e:
            logger.error(f"Error fetching profile for '{username}': {e}")
            return None

    def _format_tweets(self, raw_tweets: dict) -> list[dict]:
        """Format raw ntscraper output into standardized dicts."""
        results = []
        if not raw_tweets or "tweets" not in raw_tweets:
            return results

        for tweet in raw_tweets["tweets"]:
            try:
                results.append({
                    "text": tweet.get("text", ""),
                    "date": tweet.get("date", "Unknown"),
                    "url": tweet.get("link", ""),
                    "likes": tweet.get("stats", {}).get("likes", 0),
                    "comments": tweet.get("stats", {}).get("comments", 0),
                    "retweets": tweet.get("stats", {}).get("retweets", 0),
                    "source": "twitter",
                })
            except (KeyError, TypeError):
                continue

        return results
