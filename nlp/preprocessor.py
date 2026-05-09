"""
Text Preprocessing Module.

Cleans and normalizes raw text from news articles and tweets
for downstream NLP tasks (sentiment analysis, NER, classification).
"""

import re
import logging

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

logger = logging.getLogger(__name__)

# Download required NLTK data (once)
for resource in ["stopwords", "wordnet", "punkt", "punkt_tab"]:
    try:
        nltk.download(resource, quiet=True)
    except Exception:
        pass


class TextPreprocessor:
    """
    Pipeline for cleaning and normalizing text data.
    Handles URLs, mentions, hashtags, special characters,
    stopword removal, and lemmatization.
    """

    def __init__(self, remove_stopwords=True, lemmatize=True):
        self.remove_stopwords = remove_stopwords
        self.lemmatize = lemmatize
        self._stop_words = set(stopwords.words("english"))
        self._lemmatizer = WordNetLemmatizer()

        # Add domain-specific words to keep (don't remove as stopwords)
        self._important_words = {
            "not", "no", "very", "never", "only", "more", "most",
            "few", "many", "all", "each", "every", "against",
            "above", "below", "between", "under", "over"
        }
        self._stop_words -= self._important_words

    def clean(self, text: str) -> str:
        """
        Full cleaning pipeline for text.

        Args:
            text: Raw text to clean.

        Returns:
            Cleaned and normalized text.
        """
        if not text:
            return ""

        text = self._remove_urls(text)
        text = self._remove_mentions(text)
        text = self._remove_hashtag_symbols(text)
        text = self._normalize_whitespace(text)
        return text.strip()

    def clean_for_analysis(self, text: str) -> str:
        """
        Deep cleaning for ML/analysis: lowercase, remove punctuation,
        optional stopword removal and lemmatization.

        Args:
            text: Text to process.

        Returns:
            Deeply cleaned text suitable for NLP analysis.
        """
        text = self.clean(text)
        text = re.sub(r"[^a-zA-Z\s]", " ", text)
        text = text.lower()

        tokens = text.split()

        if self.remove_stopwords:
            tokens = [w for w in tokens if w not in self._stop_words]

        if self.lemmatize:
            tokens = [self._lemmatizer.lemmatize(w) for w in tokens]

        # Remove very short tokens
        tokens = [w for w in tokens if len(w) > 1]

        return " ".join(tokens)

    def extract_sentences(self, text: str) -> list[str]:
        """Split text into sentences using NLTK."""
        try:
            return nltk.sent_tokenize(text)
        except Exception:
            # Fallback to simple splitting
            return [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]

    # ── Private helpers ──────────────────────────────────────────────────

    @staticmethod
    def _remove_urls(text: str) -> str:
        return re.sub(r"https?://\S+|www\.\S+", "", text)

    @staticmethod
    def _remove_mentions(text: str) -> str:
        return re.sub(r"@\S+", "", text)

    @staticmethod
    def _remove_hashtag_symbols(text: str) -> str:
        """Remove # symbol but keep the word."""
        return re.sub(r"#(\S+)", r"\1", text)

    @staticmethod
    def _normalize_whitespace(text: str) -> str:
        return re.sub(r"\s+", " ", text)
