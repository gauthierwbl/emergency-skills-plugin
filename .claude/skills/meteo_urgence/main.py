import requests
import sys
import json

VILLE = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Paris"

geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={VILLE}&count=1&language=fr&format=json"
geo_response = requests.get(geo_url).json()

if "results" not in geo_response:
    print(json.dumps({"error": "Ville introuvable"}))
    sys.exit(1)

result = geo_response["results"][0]

lat = result["latitude"]
lon = result["longitude"]
name = result["name"]
country = result.get("country", "")

weather_url = (
    f"https://api.open-meteo.com/v1/forecast?"
    f"latitude={lat}&longitude={lon}"
    f"&current=temperature_2m,wind_speed_10m"
)

weather_response = requests.get(weather_url).json()

output = {
    "ville": name,
    "pays": country,
    "latitude": lat,
    "longitude": lon,
    "temperature": weather_response["current"]["temperature_2m"],
    "vent_km_h": weather_response["current"]["wind_speed_10m"]
}

print(json.dumps(output, ensure_ascii=False, indent=2))