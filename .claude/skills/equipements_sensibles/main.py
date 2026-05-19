import requests
import sys
import json
import math

args = sys.argv[1:]

if len(args) < 2:
    print(json.dumps({
        "error": "Latitude et longitude requises",
        "usage": "python main.py <latitude> <longitude> [rayon_metres]"
    }, ensure_ascii=False, indent=2))
    sys.exit(1)

latitude = float(args[0])
longitude = float(args[1])
rayon = int(args[2]) if len(args) >= 3 else 500

def distance_m(lat1, lon1, lat2, lon2):
    r = 6371000

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1)
        * math.cos(phi2)
        * math.sin(d_lambda / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return round(r * c)

overpass_query = f"""
[out:json][timeout:20];
(
  node["amenity"="hospital"](around:{rayon},{latitude},{longitude});
  node["amenity"="clinic"](around:{rayon},{latitude},{longitude});
  node["amenity"="pharmacy"](around:{rayon},{latitude},{longitude});
  node["amenity"="school"](around:{rayon},{latitude},{longitude});
  node["amenity"="fire_station"](around:{rayon},{latitude},{longitude});
  node["amenity"="police"](around:{rayon},{latitude},{longitude});
);
out body;
"""

url = "https://overpass-api.de/api/interpreter"

headers = {
    "User-Agent": "emergency-skills-plugin/1.0 student-project"
}

try:
    response = requests.post(
        url,
        data={"data": overpass_query},
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

except requests.RequestException as e:
    print(json.dumps({
        "error": "Erreur lors de l'appel à Overpass API",
        "details": str(e)
    }, ensure_ascii=False, indent=2))

    sys.exit(1)

equipements = []

for element in data.get("elements", []):

    tags = element.get("tags", {})

    lat = element.get("lat")
    lon = element.get("lon")

    if lat is None or lon is None:
        continue

    equipements.append({
        "nom": tags.get("name", "Nom non renseigné"),
        "type": tags.get("amenity", "inconnu"),
        "latitude": lat,
        "longitude": lon,
        "distance_m": distance_m(
            latitude,
            longitude,
            lat,
            lon
        )
    })

equipements = sorted(
    equipements,
    key=lambda x: x["distance_m"]
)

output = {
    "centre": {
        "latitude": latitude,
        "longitude": longitude
    },
    "rayon_m": rayon,
    "nombre_equipements": len(equipements),
    "equipements": equipements[:20],
    "source": "OpenStreetMap / Overpass API"
}

print(json.dumps(output, ensure_ascii=False, indent=2))