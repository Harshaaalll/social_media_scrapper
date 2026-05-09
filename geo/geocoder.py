"""
Geocoding Module.
Converts location names to latitude/longitude coordinates using geopy.
"""

import logging
import time

logger = logging.getLogger(__name__)

try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut
    _GEOPY_AVAILABLE = True
except ImportError:
    _GEOPY_AVAILABLE = False
    logger.warning("geopy not installed. pip install geopy")


class Geocoder:
    """Geocodes location names to lat/lon, with caching and rate limiting."""

    def __init__(self, city="Hyderabad", country="India"):
        self._city = city
        self._country = country
        self._cache = {}
        if _GEOPY_AVAILABLE:
            self._geolocator = Nominatim(user_agent="road_safety_nlp_v2", timeout=10)
        else:
            self._geolocator = None

    @property
    def is_available(self):
        return self._geolocator is not None

    def geocode(self, location_name):
        """
        Geocode a location name.

        Returns:
            dict with 'lat', 'lon', 'address' or None
        """
        if not self._geolocator or not location_name:
            return None

        cache_key = location_name.lower().strip()
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            query = f"{location_name}, {self._city}, {self._country}"
            result = self._geolocator.geocode(query, timeout=10)
            if result:
                data = {
                    "lat": result.latitude,
                    "lon": result.longitude,
                    "address": result.address,
                }
                self._cache[cache_key] = data
                time.sleep(1.1)  # Nominatim rate limit: 1 req/sec
                return data
        except Exception as e:
            logger.debug(f"Geocoding failed for '{location_name}': {e}")

        self._cache[cache_key] = None
        return None

    def geocode_batch(self, locations):
        """Geocode a list of locations. Returns list of results (may contain None)."""
        return [self.geocode(loc) for loc in locations]
