#!/usr/bin/env python3
"""
weather.py — single-file weather CLI
=====================================
No API key needed. Uses Open-Meteo (free & open).

Setup:
    pip install requests
    python weather.py London
    python weather.py "New York" --refresh
    python weather.py Tokyo --json
"""

import argparse
import json
import logging
import sys
import time
from dataclasses import dataclass, field
from typing import Optional

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    sys.exit("Missing dependency. Run:  pip install requests")


# ─────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────

GEO_URL  = "https://geocoding-api.open-meteo.com/v1/search"
WX_URL   = "https://api.open-meteo.com/v1/forecast"
CACHE_TTL     = 300   # seconds
REQUEST_TIMEOUT = 10  # seconds

WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Icy fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain",   63: "Moderate rain",    65: "Heavy rain",
    71: "Slight snow",   73: "Moderate snow",    75: "Heavy snow",
    80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
    95: "Thunderstorm",  96: "Thunderstorm w/ hail", 99: "Thunderstorm w/ heavy hail",
}


# ─────────────────────────────────────────────
#  Exceptions
# ─────────────────────────────────────────────

class WeatherError(Exception):        pass
class CityNotFoundError(WeatherError): pass
class WeatherFetchError(WeatherError): pass
class InvalidResponseError(WeatherError): pass


# ─────────────────────────────────────────────
#  HTTP session (retries + backoff)
# ─────────────────────────────────────────────

def _make_session() -> "requests.Session":
    s = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods={"GET"},
    )
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.headers["Accept"] = "application/json"
    return s

_SESSION = _make_session()


# ─────────────────────────────────────────────
#  Geocoding  (city name → lat/lon)
# ─────────────────────────────────────────────

@dataclass(frozen=True)
class Coords:
    lat: float
    lon: float
    city: str
    country: str

def _geocode(city: str) -> Coords:
    try:
        r = _SESSION.get(
            GEO_URL,
            params={"name": city, "count": 1, "language": "en", "format": "json"},
            timeout=REQUEST_TIMEOUT,
        )
        r.raise_for_status()
    except requests.exceptions.Timeout:
        raise WeatherFetchError("Request timed out — check your connection.")
    except requests.exceptions.ConnectionError as e:
        raise WeatherFetchError(f"Network error: {e}")
    except requests.exceptions.HTTPError as e:
        raise WeatherFetchError(f"Geocoding HTTP error: {e}")

    hits = r.json().get("results")
    if not hits:
        raise CityNotFoundError(
            f"City not found: {city!r}. Check spelling or try a nearby major city."
        )
    h = hits[0]
    return Coords(lat=h["latitude"], lon=h["longitude"],
                  city=h.get("name", city), country=h.get("country", ""))


# ─────────────────────────────────────────────
#  Weather fetch  (lat/lon → conditions)
# ─────────────────────────────────────────────

@dataclass
class WeatherResult:
    temperature: float
    humidity: int
    description: str
    wind_speed: float
    city: str
    country: str
    fetched_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "city":        self.city,
            "country":     self.country,
            "temperature": self.temperature,
            "humidity":    self.humidity,
            "description": self.description,
            "wind_speed":  self.wind_speed,
            "fetched_at":  self.fetched_at,
        }

def _fetch_weather(coords: Coords) -> WeatherResult:
    try:
        r = _SESSION.get(
            WX_URL,
            params={
                "latitude":        coords.lat,
                "longitude":       coords.lon,
                "current":         "temperature_2m,relative_humidity_2m,weathercode,wind_speed_10m",
                "wind_speed_unit": "kmh",
                "timezone":        "auto",
            },
            timeout=REQUEST_TIMEOUT,
        )
        r.raise_for_status()
    except requests.exceptions.Timeout:
        raise WeatherFetchError("Weather request timed out.")
    except requests.exceptions.ConnectionError as e:
        raise WeatherFetchError(f"Network error: {e}")
    except requests.exceptions.HTTPError as e:
        raise WeatherFetchError(f"Weather API error: {e}")

    try:
        cur  = r.json()["current"]
        code = int(cur["weathercode"])
        return WeatherResult(
            temperature  = round(cur["temperature_2m"], 1),
            humidity     = int(cur["relative_humidity_2m"]),
            description  = WMO_CODES.get(code, f"Code {code}"),
            wind_speed   = round(cur["wind_speed_10m"], 1),
            city         = coords.city,
            country      = coords.country,
        )
    except (KeyError, TypeError, ValueError) as e:
        raise InvalidResponseError(f"Unexpected API response: {e}")


# ─────────────────────────────────────────────
#  In-memory cache  (5-minute TTL)
# ─────────────────────────────────────────────

_CACHE: dict[str, WeatherResult] = {}

def _cache_get(city: str) -> Optional[WeatherResult]:
    entry = _CACHE.get(city.strip().lower())
    if entry and (time.time() - entry.fetched_at) < CACHE_TTL:
        return entry
    return None

def _cache_set(city: str, result: WeatherResult) -> None:
    _CACHE[city.strip().lower()] = result


# ─────────────────────────────────────────────
#  Public API
# ─────────────────────────────────────────────

def get_weather(city: str, force_refresh: bool = False) -> dict:
    """
    Returns dict: city, country, temperature, humidity,
                  description, wind_speed, fetched_at, cached
    """
    if not city or not city.strip():
        raise ValueError("City name must be a non-empty string.")

    if not force_refresh:
        hit = _cache_get(city)
        if hit:
            return {**hit.to_dict(), "cached": True}

    coords = _geocode(city)
    result = _fetch_weather(coords)
    _cache_set(city, result)
    return {**result.to_dict(), "cached": False}


# ─────────────────────────────────────────────
#  CLI
# ─────────────────────────────────────────────

def _render(data: dict) -> str:
    tag = " (cached)" if data.get("cached") else ""
    return (
        f"\n{'─'*40}\n"
        f"  📍  {data['city']}, {data['country']}{tag}\n"
        f"{'─'*40}\n"
        f"  🌡   Temperature : {data['temperature']} °C\n"
        f"  💧  Humidity    : {data['humidity']} %\n"
        f"  🌤   Conditions  : {data['description']}\n"
        f"  💨  Wind speed  : {data['wind_speed']} km/h\n"
        f"{'─'*40}\n"
    )

def main():
    p = argparse.ArgumentParser(
        prog="weather",
        description="Get current weather for any city (Open-Meteo, no API key).",
    )
    p.add_argument("city",        help='e.g. "London" or "New York"')
    p.add_argument("-r", "--refresh", action="store_true", help="Bypass cache")
    p.add_argument("-j", "--json",    action="store_true", help="Raw JSON output")
    p.add_argument("-v", "--verbose", action="store_true", help="Debug logging")
    args = p.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

    try:
        data = get_weather(args.city, force_refresh=args.refresh)
    except CityNotFoundError as e:
        sys.exit(f"❌  {e}")
    except WeatherFetchError as e:
        sys.exit(f"🌐  {e}")
    except InvalidResponseError as e:
        sys.exit(f"⚠️   {e}")
    except ValueError as e:
        sys.exit(f"❗  {e}")

    print(json.dumps(data, indent=2, default=str) if args.json else _render(data))


if __name__ == "__main__":
    main()
