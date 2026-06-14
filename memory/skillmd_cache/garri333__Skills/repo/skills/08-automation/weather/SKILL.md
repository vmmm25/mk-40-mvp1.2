---
name: weather
version: 1.0.0
description: Obtener clima actual y predicciones meteorológicas en lenguaje natural. Usa cuando necesites información del tiempo para tomar decisiones o incluirla en contenido.
tags: [weather, forecast, api, openweathermap, wttr, geolocation]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Weather Skill

## Opción 1: wttr.in (sin API key, instantáneo)

```bash
# En terminal — sin configuración
curl wttr.in/Barcelona
curl wttr.in/Madrid?format=3          # Formato compacto: "Madrid: ⛅️  +15°C"
curl wttr.in/London?format=json       # JSON completo
curl wttr.in/~"Sagrada+Familia"       # Por nombre de lugar

# Con emojis bonitos
curl "wttr.in/Barcelona?format=🌡️+%t\n🌧️+%p\n💨+%w"
```

```python
import requests

def get_weather_simple(city: str) -> str:
    """Obtener clima en formato texto legible (sin API key)"""
    response = requests.get(f"https://wttr.in/{city}?format=3")
    return response.text.strip()

def get_weather_json(city: str) -> dict:
    """Obtener clima completo en JSON"""
    response = requests.get(f"https://wttr.in/{city}?format=j1")
    data = response.json()
    
    current = data["current_condition"][0]
    return {
        "city": city,
        "temp_c": int(current["temp_C"]),
        "feels_like_c": int(current["FeelsLikeC"]),
        "humidity": int(current["humidity"]),
        "description": current["weatherDesc"][0]["value"],
        "wind_kmh": int(current["windspeedKmph"]),
    }

# Uso
print(get_weather_simple("Barcelona"))   # "Barcelona: ⛅️  +18°C"
print(get_weather_json("Madrid"))
```

## Opción 2: OpenWeatherMap (API key gratuita)

```python
# pip install pyowm
# Variables: OPENWEATHER_API_KEY (free tier: 1000 calls/day)
import os
import requests

OWM_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5"

def get_current_weather(city: str = None, lat: float = None, lon: float = None) -> dict:
    """Clima actual por ciudad o coordenadas"""
    params = {"appid": OWM_KEY, "units": "metric", "lang": "es"}
    
    if city:
        params["q"] = city
    elif lat and lon:
        params["lat"] = lat
        params["lon"] = lon
    else:
        raise ValueError("Provide city or coordinates")
    
    response = requests.get(f"{BASE_URL}/weather", params=params)
    data = response.json()
    
    return {
        "city": data["name"],
        "country": data["sys"]["country"],
        "temp_c": round(data["main"]["temp"], 1),
        "feels_like": round(data["main"]["feels_like"], 1),
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"],
        "wind_speed": data["wind"]["speed"],
        "icon": data["weather"][0]["icon"],
        "sunrise": data["sys"]["sunrise"],
        "sunset": data["sys"]["sunset"],
    }


def get_forecast_5days(city: str) -> list:
    """Predicción para los próximos 5 días (cada 3 horas)"""
    params = {"q": city, "appid": OWM_KEY, "units": "metric", "lang": "es"}
    response = requests.get(f"{BASE_URL}/forecast", params=params)
    data = response.json()
    
    # Agrupar por día
    from collections import defaultdict
    from datetime import datetime
    
    days = defaultdict(list)
    for item in data["list"]:
        date = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
        days[date].append(item)
    
    forecast = []
    for date, items in sorted(days.items()):
        temps = [i["main"]["temp"] for i in items]
        forecast.append({
            "date": date,
            "temp_min": round(min(temps), 1),
            "temp_max": round(max(temps), 1),
            "description": items[len(items)//2]["weather"][0]["description"],
            "humidity": sum(i["main"]["humidity"] for i in items) // len(items),
        })
    
    return forecast[:5]
```

## Opción 3: Open-Meteo (sin API key, alta precisión)

```python
import requests
from datetime import datetime

def get_forecast_open_meteo(lat: float, lon: float, days: int = 7) -> dict:
    """Predicción gratuita de alta calidad desde Open-Meteo"""
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum",
                  "wind_speed_10m_max", "weathercode"],
        "current_weather": True,
        "forecast_days": days,
        "timezone": "auto",
    }
    
    response = requests.get("https://api.open-meteo.com/v1/forecast", params=params)
    data = response.json()
    
    daily = data["daily"]
    forecast = []
    for i in range(len(daily["time"])):
        forecast.append({
            "date": daily["time"][i],
            "temp_max": daily["temperature_2m_max"][i],
            "temp_min": daily["temperature_2m_min"][i],
            "precipitation_mm": daily["precipitation_sum"][i],
            "wind_max_kmh": daily["wind_speed_10m_max"][i],
        })
    
    return {
        "current": data["current_weather"],
        "forecast": forecast,
    }


def geocode(city: str) -> tuple[float, float]:
    """Obtener coordenadas de una ciudad"""
    response = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1, "language": "es"}
    )
    results = response.json().get("results", [])
    if not results:
        raise ValueError(f"Ciudad no encontrada: {city}")
    return results[0]["latitude"], results[0]["longitude"]


# Uso completo sin API key
def weather_for_city(city: str) -> dict:
    lat, lon = geocode(city)
    return get_forecast_open_meteo(lat, lon)

forecast = weather_for_city("Barcelona")
```

## Integración típica en agente

```python
def should_bring_umbrella(city: str) -> str:
    """¿Necesito paraguas? Respuesta en lenguaje natural"""
    data = get_weather_json(city)
    
    if "rain" in data["description"].lower() or "lluvia" in data["description"].lower():
        return f"☔ Sí, se espera {data['description']} en {city}. Lleva paraguas."
    elif "cloud" in data["description"].lower() or "nube" in data["description"].lower():
        return f"🌤️ Podría llover en {city}. Mejor llevar paraguas por si acaso."
    else:
        return f"☀️ Buen tiempo en {city}: {data['description']}. No necesitas paraguas."
```

## Referencias
- [wttr.in](https://wttr.in/) — Weather en terminal, sin setup
- [Open-Meteo](https://open-meteo.com/) — API gratuita, sin key, alta calidad
- [OpenWeatherMap](https://openweathermap.org/api) — API con free tier generoso
