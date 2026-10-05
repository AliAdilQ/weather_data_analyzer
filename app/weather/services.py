"""Live OpenWeather retrieval with explicit, deterministic demo fallback."""

from datetime import datetime, timezone
import hashlib
import math
import requests
from flask import current_app

CITIES = {
    "Yogyakarta": ("ID", 28, 79),
    "Jakarta": ("ID", 31, 75),
    "Lahore": ("PK", 30, 48),
    "Islamabad": ("PK", 25, 55),
    "London": ("GB", 16, 72),
    "New York": ("US", 21, 62),
    "Tokyo": ("JP", 24, 68),
    "Dubai": ("AE", 36, 40),
}


def demo_weather(city, when=None):
    """Return a reproducible synthetic observation for a supported city."""
    canonical = next(
        (name for name in CITIES if name.casefold() == city.strip().casefold()), None
    )
    if not canonical:
        raise ValueError(
            "City unavailable in demo mode. Choose one of the eight suggested cities."
        )
    when = when or datetime.now(timezone.utc).replace(tzinfo=None)
    country, base, humidity = CITIES[canonical]
    phase = int(hashlib.sha256(canonical.encode()).hexdigest()[:8], 16) % 20
    variation = math.sin(when.timetuple().tm_yday / 2 + phase)
    temp = round(base + 3 * variation, 1)
    condition = ["Clear", "Clouds", "Rain"][(when.day + phase) % 3]
    return dict(
        city=canonical,
        country=country,
        temperature=temp,
        feels_like=round(temp + 1.2, 1),
        temp_min=temp - 2,
        temp_max=temp + 2,
        humidity=min(100, max(0, round(humidity + 8 * variation))),
        pressure=1012 + round(4 * variation),
        wind_speed=round(3 + abs(variation) * 3, 1),
        visibility=10000 if condition != "Rain" else 6000,
        condition=condition,
        description={
            "Clear": "Clear sky",
            "Clouds": "Scattered clouds",
            "Rain": "Light rain",
        }[condition],
        icon="",
        recorded_at=when,
        source="Demo",
    )


def get_weather(city):
    """Resolve city coordinates, fetch metric weather, or safely use demo data."""
    key = current_app.config["WEATHER_API_KEY"]
    if key and not current_app.config["DEMO_MODE"]:
        try:
            geo = requests.get(
                "https://api.openweathermap.org/geo/1.0/direct",
                params={"q": city, "limit": 1, "appid": key},
                timeout=8,
            )
            geo.raise_for_status()
            places = geo.json()
            if not places:
                raise ValueError(
                    "City not found. Check the spelling or include a country code."
                )
            place = places[0]
            response = requests.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={
                    "lat": place["lat"],
                    "lon": place["lon"],
                    "appid": key,
                    "units": "metric",
                },
                timeout=8,
            )
            response.raise_for_status()
            data = response.json()
            main, weather = data["main"], data["weather"][0]
            return dict(
                city=place["name"],
                country=place["country"],
                temperature=main["temp"],
                feels_like=main["feels_like"],
                temp_min=main.get("temp_min", main["temp"]),
                temp_max=main.get("temp_max", main["temp"]),
                humidity=main["humidity"],
                pressure=main["pressure"],
                wind_speed=data["wind"]["speed"],
                visibility=data.get("visibility", 0),
                condition=weather["main"],
                description=weather["description"],
                icon=weather.get("icon", ""),
                recorded_at=datetime.fromtimestamp(data["dt"], timezone.utc).replace(
                    tzinfo=None
                ),
                source="API",
            )
        except (requests.RequestException, KeyError, TypeError, IndexError):
            current_app.logger.warning(
                "Weather provider unavailable; attempting demo fallback."
            )
    return demo_weather(city)
