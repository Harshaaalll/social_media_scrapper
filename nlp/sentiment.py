"""
Sentiment Analysis Module.
Uses VADER for sentiment scoring of road safety related text.
"""

import logging

logger = logging.getLogger(__name__)

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    _VADER_AVAILABLE = True
except ImportError:
    _VADER_AVAILABLE = False
    logger.warning("vaderSentiment not installed. pip install vaderSentiment")


class SentimentAnalyzer:
    """Performs sentiment analysis using VADER."""

    POSITIVE_THRESHOLD = 0.05
    NEGATIVE_THRESHOLD = -0.05

    def __init__(self):
        self._analyzer = SentimentIntensityAnalyzer() if _VADER_AVAILABLE else None

    @property
    def is_available(self):
        return self._analyzer is not None

    def analyze(self, text):
        if not self._analyzer or not text:
            return {"compound": 0.0, "positive": 0.0, "negative": 0.0, "neutral": 1.0, "label": "neutral"}
        scores = self._analyzer.polarity_scores(text)
        return {
            "compound": scores["compound"],
            "positive": scores["pos"],
            "negative": scores["neg"],
            "neutral": scores["neu"],
            "label": self._categorize(scores["compound"]),
        }

    def analyze_batch(self, texts):
        return [self.analyze(t) for t in texts]

    def get_compound_score(self, text):
        if not self._analyzer or not text:
            return 0.0
        return self._analyzer.polarity_scores(text)["compound"]

    def _categorize(self, compound):
        if compound >= self.POSITIVE_THRESHOLD:
            return "positive"
        elif compound <= self.NEGATIVE_THRESHOLD:
            return "negative"
        return "neutral"
