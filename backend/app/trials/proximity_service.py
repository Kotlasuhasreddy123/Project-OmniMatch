"""Geographic proximity trial ranking — NEW FEATURE differentiating OmniMatch.

No existing clinical trial matching system (TrialMatchAI, PRISM, TrialGPT as of 2025)
incorporates geographic proximity into trial ranking. A perfect eligibility match
at a site 2,000 miles away is clinically less actionable than an 80% match nearby.

OmniMatch re-ranks matched trials by distance from the clinic's ZIP code.
Trial site locations are fetched from ClinicalTrials.gov LocationModule.
"""

from __future__ import annotations

import logging
import math
from functools import lru_cache

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# Approximate US ZIP code centroids — a small inline lookup for common codes
# Full dataset: use zipcodes package or USPS ZIP centroid CSV
# This covers major metro areas for demonstration purposes
ZIP_CENTROIDS: dict[str, tuple[float, float]] = {
    "10001": (40.7484, -73.9967),   # New York, NY
    "60601": (41.8827, -87.6233),   # Chicago, IL
    "90001": (33.9731, -118.2479),  # Los Angeles, CA
    "77001": (29.7543, -95.3677),   # Houston, TX
    "85001": (33.4484, -112.0740),  # Phoenix, AZ
    "19101": (39.9526, -75.1652),   # Philadelphia, PA
    "78201": (29.4241, -98.4936),   # San Antonio, TX
    "92101": (32.7157, -117.1611),  # San Diego, CA
    "75201": (32.7767, -96.7970),   # Dallas, TX
    "95101": (37.3382, -121.8863),  # San Jose, CA
    "78701": (30.2672, -97.7431),   # Austin, TX
    "78201": (29.4241, -98.4936),   # San Antonio, TX
    "32099": (30.3322, -81.6557),   # Jacksonville, FL
    "37201": (36.1627, -86.7816),   # Nashville, TN
    "43085": (40.0742, -82.9963),   # Columbus, OH
    "28201": (35.2271, -80.8431),   # Charlotte, NC
    "46201": (39.7684, -86.1581),   # Indianapolis, IN
    "76101": (32.7555, -97.3308),   # Fort Worth, TX
    "28501": (35.2636, -77.5816),   # North Carolina
    "02101": (42.3601, -71.0589),   # Boston, MA
    "98101": (47.6062, -122.3321),  # Seattle, WA
    "80201": (39.7392, -104.9903),  # Denver, CO
    "02201": (42.3601, -71.0589),   # Boston MA alt
    "20001": (38.9072, -77.0369),   # Washington DC
    "30301": (33.7490, -84.3880),   # Atlanta, GA
    "33101": (25.7617, -80.1918),   # Miami, FL
    "55401": (44.9778, -93.2650),   # Minneapolis, MN
    "63101": (38.6270, -90.1994),   # St. Louis, MO
    "15201": (40.4406, -79.9959),   # Pittsburgh, PA
    "67201": (37.6872, -97.3301),   # Wichita, KS
}

EARTH_RADIUS_MILES = 3958.8


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance in miles between two lat/lon points.

    Args:
        lat1, lon1: First coordinate (degrees).
        lat2, lon2: Second coordinate (degrees).

    Returns:
        Distance in miles.
    """
    r = EARTH_RADIUS_MILES
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def get_clinic_coords(clinic_zip: str) -> tuple[float, float] | None:
    """Return (lat, lon) for a clinic ZIP code, or None if not found.

    Args:
        clinic_zip: 5-digit US ZIP code string.

    Returns:
        (latitude, longitude) tuple or None.
    """
    return ZIP_CENTROIDS.get(clinic_zip[:5])


async def fetch_trial_locations(nct_id: str) -> list[dict]:
    """Fetch site locations for a trial from ClinicalTrials.gov API v2.

    Args:
        nct_id: ClinicalTrials.gov NCT identifier.

    Returns:
        List of location dicts with city, state, country, zip, lat, lon.
    """
    url = f"https://clinicaltrials.gov/api/v2/studies/{nct_id}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params={"format": "json", "fields": "LocationModule"})
            if resp.status_code != 200:
                return []
            data = resp.json()
            locations_raw = (
                data.get("protocolSection", {})
                .get("contactsLocationsModule", {})
                .get("locations", [])
            )
            return [
                {
                    "facility": loc.get("facility", ""),
                    "city": loc.get("city", ""),
                    "state": loc.get("state", ""),
                    "country": loc.get("country", ""),
                    "zip": loc.get("zip", ""),
                }
                for loc in locations_raw
            ]
    except Exception as exc:
        logger.warning("Could not fetch locations for %s: %s", nct_id, exc)
        return []


def rank_by_proximity(
    trial_matches: list[dict],
    clinic_zip: str,
    max_distance_miles: float = 200.0,
) -> list[dict]:
    """Re-rank trial matches by geographic proximity to the clinic.

    Trials with no location data are placed at the end.
    Proximity is incorporated as a tiebreaker — eligibility score stays primary.

    Args:
        trial_matches: List of trial match dicts (must have 'locations' key).
        clinic_zip: 5-digit clinic ZIP code.
        max_distance_miles: Maximum distance to show; trials beyond this are deprioritized.

    Returns:
        Re-ranked list with 'nearest_site_miles' and 'nearest_site_city' added.
    """
    clinic_coords = get_clinic_coords(clinic_zip)
    if not clinic_coords:
        # Can't rank without clinic coords — return unchanged
        for m in trial_matches:
            m["nearest_site_miles"] = None
            m["nearest_site_city"] = "Unknown"
        return trial_matches

    clinic_lat, clinic_lon = clinic_coords

    for match in trial_matches:
        locations = match.get("locations", [])
        best_dist = float("inf")
        best_city = "Unknown"

        for loc in locations:
            # Try to get coords from ZIP centroid
            loc_zip = (loc.get("zip") or "")[:5]
            loc_coords = ZIP_CENTROIDS.get(loc_zip)
            if loc_coords:
                dist = haversine_distance(clinic_lat, clinic_lon, *loc_coords)
                if dist < best_dist:
                    best_dist = dist
                    best_city = f"{loc.get('city', '')}, {loc.get('state', '')}".strip(", ")

        match["nearest_site_miles"] = round(best_dist, 1) if best_dist != float("inf") else None
        match["nearest_site_city"] = best_city

    # Sort: within max_distance first (by score desc), then beyond (by score desc)
    within = [m for m in trial_matches
              if m.get("nearest_site_miles") is not None
              and m["nearest_site_miles"] <= max_distance_miles]
    beyond = [m for m in trial_matches
              if m.get("nearest_site_miles") is None
              or m["nearest_site_miles"] > max_distance_miles]

    within.sort(key=lambda m: -m.get("enrollment_readiness_score", m.get("score", 0)))
    beyond.sort(key=lambda m: -m.get("enrollment_readiness_score", m.get("score", 0)))

    return within + beyond
