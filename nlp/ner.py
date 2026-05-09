"""
Named Entity Recognition Module.
Uses SpaCy to extract location entities from article text.
"""

import logging
from config.settings import SPACY_MODEL, EXCLUDED_LOCATIONS

logger = logging.getLogger(__name__)

try:
    import spacy
    _nlp = spacy.load(SPACY_MODEL)
    _SPACY_AVAILABLE = True
except (ImportError, OSError):
    _SPACY_AVAILABLE = False
    _nlp = None
    logger.warning(f"SpaCy model '{SPACY_MODEL}' not found. Run: python -m spacy download {SPACY_MODEL}")


class LocationExtractor:
    """Extracts geographical locations from text using SpaCy NER."""

    def __init__(self):
        self._nlp = _nlp

    @property
    def is_available(self):
        return _SPACY_AVAILABLE

    def extract_locations(self, text):
        """Extract unique location names from text."""
        if not self._nlp or not text:
            return []
        doc = self._nlp(text[:100000])  # Limit text length for performance
        locations = set()
        for ent in doc.ents:
            if ent.label_ in ("GPE", "LOC", "FAC"):
                name = ent.text.strip()
                if name.lower() not in EXCLUDED_LOCATIONS and len(name) > 1:
                    locations.add(name)
        return list(locations)

    def extract_all_entities(self, text):
        """Extract all named entities grouped by type."""
        if not self._nlp or not text:
            return {}
        doc = self._nlp(text[:100000])
        entities = {}
        for ent in doc.ents:
            label = ent.label_
            if label not in entities:
                entities[label] = []
            entities[label].append(ent.text.strip())
        # Deduplicate
        return {k: list(set(v)) for k, v in entities.items()}
