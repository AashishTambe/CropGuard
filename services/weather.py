"""Open-Meteo weather with demo fallback. Never raises to the UI."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import requests

DEMO_BY_DISTRICT = {
    "Nashik": {"temperature_c": 25.0, "humidity": 82, "rainfall_mm": 8.4, "wind_kmh": 11.0, "condition": "Humid with recent rain"},
    "Pune": {"temperature_c": 27.2, "humidity": 68, "rainfall_mm": 2.1, "wind_kmh": 14.0, "condition": "Partly cloudy"},
    "Nagpur": {"temperature_c": 30.1, "humidity": 61, "rainfall_mm": 1.0, "wind_kmh": 12.0, "condition": "Warm and dry-ish"},
    "Amravati": {"temperature_c": 29.4, "humidity": 64, "rainfall_mm": 1.6, "wind_kmh": 10.0, "condition": "Warm"},
    "Latur": {"temperature_c": 28.6, "humidity": 58, "rainfall_mm": 0.4, "wind_kmh": 13.0, "condition": "Mostly clear"},
    "Solapur": {"temperature_c": 31.0, "humidity": 52, "rainfall_mm": 0.2, "wind_kmh": 15.0, "condition": "Hot and dry"},
    "Kolhapur": {"temperature_c": 26.4, "humidity": 80, "rainfall_mm": 7.2, "wind_kmh": 9.0, "condition": "Humid"},
}


def demo_weather(district: str = "Nashik") -> dict[str, Any]:
    base = DEMO_BY_DISTRICT.get(district, DEMO_BY_DISTRICT["Nashik"]).copy()
    base.update({"source": "demo", "district": district, "fetched_at": datetime.utcnow().isoformat(timespec="seconds") + "Z"})
    return base


def fetch_weather(lat: float, lon: float, district: str = "Nashik", timeout: float = 6.0) -> dict[str, Any]:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m",
        "daily": "precipitation_sum",
        "timezone": "Asia/Kolkata",
        "forecast_days": 2,
    }
    try:
        resp = requests.get(url, params=params, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        current = data.get("current") or {}
        daily = data.get("daily") or {}
        rain = 0.0
        precip = daily.get("precipitation_sum") or []
        if precip:
            rain = float(precip[0] or 0.0)
        code = int(current.get("weather_code") or 0)
        result = {
            "temperature_c": float(current.get("temperature_2m") or 26.0),
            "humidity": float(current.get("relative_humidity_2m") or 70.0),
            "rainfall_mm": rain,
            "wind_kmh": float(current.get("wind_speed_10m") or 8.0),
            "condition": _code_to_text(code),
            "source": "open-meteo",
            "district": district,
            "fetched_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        }
        return result
    except Exception:
        w = demo_weather(district)
        w["fallback_reason"] = "Weather service unavailable. Showing demo weather data."
        return w


def _code_to_text(code: int) -> str:
    if code == 0:
        return "Clear"
    if code <= 3:
        return "Partly cloudy"
    if code <= 48:
        return "Foggy / hazy"
    if code <= 67:
        return "Rain"
    if code <= 77:
        return "Wintry precipitation"
    if code <= 82:
        return "Rain showers"
    if code <= 99:
        return "Thunderstorm"
    return "Unspecified"


def recent_rain_label(mm: float) -> str:
    if mm >= 8:
        return "High"
    if mm >= 2:
        return "Moderate"
    return "Low"
