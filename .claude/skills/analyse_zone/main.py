import requests
import sys
import json
import math

adresse = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""

if not adresse:
    print(json.dumps({"error": "Aucune adresse fournie"}, ensure_ascii=False, indent=2))
    sys.exit(1)


def distance_m(lat1, lon1, lat2, lon2):
    r = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(r * c)


def geocoder(adresse):
    url = "https://api-adresse.data.gouv.fr/search/"
    params = {"q": adresse, "limit": 1}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    if not data.get("features"):
        return None

    feature = data["features"][0]
    props = feature["properties"]
    longitude, latitude = feature["geometry"]["coordinates"]

    return {
        "adresse_trouvee": props.get("label"),
        "commune": props.get("city"),
        "code_postal": props.get("postcode"),
        "code_commune": props.get("citycode"),
        "latitude": latitude,
        "longitude": longitude,
        "score": props.get("score")
    }


def meteo(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,wind_speed_10m,precipitation,rain"
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    current = data.get("current", {})

    return {
        "temperature": current.get("temperature_2m"),
        "vent_km_h": current.get("wind_speed_10m"),
        "precipitation_mm": current.get("precipitation"),
        "pluie_mm": current.get("rain")
    }


def risques(code_insee):
    url = "https://www.georisques.gouv.fr/api/v1/gaspar/risques"
    params = {"code_insee": code_insee}
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    if data.get("results", 0) == 0:
        return {
            "message": "Aucun risque trouvé avec cet endpoint.",
            "endpoint": "gaspar/risques"
        }

    return {
        "nombre_resultats": data.get("results"),
        "donnees": data.get("data", []),
        "endpoint": "gaspar/risques"
    }


def equipements_sensibles(latitude, longitude, rayon=500):
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

    response = requests.post(
        url,
        data={"data": overpass_query},
        headers=headers,
        timeout=30
    )
    response.raise_for_status()
    data = response.json()

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
            "distance_m": distance_m(latitude, longitude, lat, lon)
        })

    return {
        "rayon_m": rayon,
        "nombre_equipements": len(equipements),
        "equipements": sorted(equipements, key=lambda x: x["distance_m"])[:10],
        "source": "OpenStreetMap / Overpass API"
    }


try:
    localisation = geocoder(adresse)

    if localisation is None:
        print(json.dumps({"error": "Adresse introuvable"}, ensure_ascii=False, indent=2))
        sys.exit(1)

    latitude = localisation["latitude"]
    longitude = localisation["longitude"]

    output = {
        "requete": adresse,
        "localisation": localisation,
        "meteo": meteo(latitude, longitude),
        "risques": risques(localisation["code_commune"]),
        "equipements_sensibles": equipements_sensibles(latitude, longitude, 500)
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))

except requests.RequestException as e:
    print(json.dumps({
        "error": "Erreur lors de l'appel à une API externe",
        "details": str(e)
    }, ensure_ascii=False, indent=2))
    sys.exit(1)