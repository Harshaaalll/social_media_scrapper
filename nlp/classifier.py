"""
Accident Severity Classifier Module.
Classifies articles into severity levels (Fatal/Severe/Moderate/Minor)
based on keyword matching and contextual analysis.
"""

import re
import logging
from config.settings import SEVERITY_KEYWORDS

logger = logging.getLogger(__name__)


class SeverityClassifier:
    """Classifies road accident severity from text content."""

    LEVELS = ["fatal", "severe", "moderate", "minor"]

    def __init__(self):
        self.severity_keywords = SEVERITY_KEYWORDS

    def classify(self, text):
        """
        Classify the severity of an accident described in text.

        Returns:
            dict with 'level', 'confidence', 'matched_keywords', 'casualty_count'
        """
        if not text:
            return {"level": "unknown", "confidence": 0.0, "matched_keywords": [], "casualty_count": 0}

        text_lower = text.lower()
        matches = {}
        for level in self.LEVELS:
            found = [kw for kw in self.severity_keywords[level] if kw in text_lower]
            matches[level] = found

        # Determine severity (highest wins)
        for level in self.LEVELS:
            if matches[level]:
                confidence = min(1.0, len(matches[level]) * 0.25)
                return {
                    "level": level,
                    "confidence": confidence,
                    "matched_keywords": matches[level],
                    "casualty_count": self._extract_casualty_count(text_lower),
                }

        return {"level": "unclassified", "confidence": 0.0, "matched_keywords": [], "casualty_count": 0}

    def classify_batch(self, texts):
        return [self.classify(t) for t in texts]

    # Word-to-number mapping for natural language
    _WORD_NUMBERS = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
        "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
        "fifteen": 15, "twenty": 20, "thirty": 30, "fifty": 50,
    }

    def _extract_casualty_count(self, text):
        """Try to extract number of casualties mentioned (digits or words)."""
        # First replace word numbers with digits for matching
        normalized = text
        for word, num in self._WORD_NUMBERS.items():
            normalized = re.sub(rf"\b{word}\b", str(num), normalized)

        patterns = [
            r"(\d+)\s*(?:people|persons?|victims?)\s*(?:killed|died|dead|deceased)",
            r"(\d+)\s*(?:killed|died|dead)",
            r"(?:killed|died|dead)\s*(\d+)",
            r"(\d+)\s*(?:injured|hurt|wounded)",
            r"death\s*toll\s*(?:of|reaches?|rises?\s*to)\s*(\d+)",
            r"(\d+)\s*(?:fatal)\s*(?:accidents?|incidents?|crashes?)",
        ]
        counts = []
        for pattern in patterns:
            found = re.findall(pattern, normalized)
            counts.extend([int(n) for n in found if n.isdigit()])
        return max(counts) if counts else 0
