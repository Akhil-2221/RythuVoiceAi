"""Weather forecasts from Open-Meteo (no API key required)."""
import requests

GEO = "https://geocoding-api.open-meteo.com/v1/search"
FC = "https://api.open-meteo.com/v1/forecast"


def _get_json(url, params):
    response = requests.get(url, params=params, timeout=15, headers={"User-Agent": "RythuVoiceAI/1.0"})
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise RuntimeError("Weather provider returned an invalid response.")
    return data


def forecast(lat=None, lon=None, place=None):
    name = place.strip() if place else None
    if (lat is None) != (lon is None):
        raise ValueError("Both latitude and longitude are required.")
    if lat is None or lon is None:
        if not name:
            raise ValueError("Provide coordinates or a village/town name.")
        geo = _get_json(GEO, {"name": name, "count": 1, "language": "en", "format": "json", "countryCode": "IN"})
        if not geo.get("results"):
            raise ValueError("Place not found in India. Try a nearby town or district name.")
        result = geo["results"][0]
        lat, lon = result["latitude"], result["longitude"]
        name = ", ".join(x for x in [result.get("name"), result.get("admin1"), result.get("country")] if x)
    if not (-90 <= float(lat) <= 90 and -180 <= float(lon) <= 180):
        raise ValueError("Invalid latitude or longitude.")

    data = _get_json(FC, {
        "latitude": lat, "longitude": lon, "timezone": "auto", "forecast_days": 3,
        "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max"
    })
    daily = data.get("daily") or {}
    required = ["time", "temperature_2m_max", "temperature_2m_min", "precipitation_sum", "precipitation_probability_max"]
    if not all(key in daily for key in required):
        raise RuntimeError("Weather provider did not return the expected forecast fields.")
    days = [{
        "date": daily["time"][i],
        "max": daily["temperature_2m_max"][i],
        "min": daily["temperature_2m_min"][i],
        "rain_mm": daily["precipitation_sum"][i],
        "rain_prob": daily["precipitation_probability_max"][i],
    } for i in range(len(daily["time"]))]
    alerts = []
    if any((d["rain_prob"] or 0) >= 60 or (d["rain_mm"] or 0) >= 10 for d in days):
        alerts.append("rain_expected")
    if any((d["max"] or 0) >= 38 for d in days):
        alerts.append("heat")
    return {"place": name or "Selected location", "current": data.get("current"), "days": days,
            "alerts": alerts, "source": "Open-Meteo"}
