import httpx
from strands import tool


@tool
def get_weather(city: str, country: str, date: str) -> str:
    """Get the weather forecast for a given city, country, and date.

    Args:
        city: The name of the city (e.g. "London").
        country: The ISO 3166-1 alpha-2 country code (e.g. "GB").
        date: The date for the forecast in YYYY-MM-DD format.

    Returns:
        A string describing the weather conditions for the given location and date.
    """
    geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_params = {"name": city, "count": 1, "language": "en", "format": "json"}

    with httpx.Client() as client:
        geo_response = client.get(geocode_url, params=geo_params)
        geo_response.raise_for_status()
        geo_data = geo_response.json()

    results = geo_data.get("results")
    if not results:
        return f"Could not find location for {city}, {country}."

    location = results[0]
    latitude = location["latitude"]
    longitude = location["longitude"]

    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
        "timezone": "auto",
        "start_date": date,
        "end_date": date,
    }

    with httpx.Client() as client:
        weather_response = client.get(weather_url, params=weather_params)
        weather_response.raise_for_status()
        weather_data = weather_response.json()

    daily = weather_data.get("daily", {})
    if not daily.get("time"):
        return f"No weather data available for {city}, {country} on {date}."

    temp_max = daily["temperature_2m_max"][0]
    temp_min = daily["temperature_2m_min"][0]
    precipitation = daily["precipitation_sum"][0]
    weathercode = daily["weathercode"][0]

    wmo_codes = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Foggy", 48: "Icy fog", 51: "Light drizzle", 53: "Moderate drizzle",
        55: "Dense drizzle", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow", 80: "Slight showers",
        81: "Moderate showers", 82: "Violent showers", 95: "Thunderstorm",
    }
    condition = wmo_codes.get(weathercode, f"Weather code {weathercode}")

    return (
        f"Weather for {city}, {country} on {date}:\n"
        f"  Condition: {condition}\n"
        f"  Temperature: {temp_min}°C – {temp_max}°C\n"
        f"  Precipitation: {precipitation} mm"
    )
