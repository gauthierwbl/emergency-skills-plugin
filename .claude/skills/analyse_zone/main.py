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
        "pluie_mm": current.get("rain"),
        "source": "Open-Meteo"
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
            "endpoint": "gaspar/risques",
            "source": "Géorisques"
        }

    return {
        "nombre_resultats": data.get("results"),
        "donnees": data.get("data", []),
        "endpoint": "gaspar/risques",
        "source": "Géorisques"
    }


def equipements_sensibles(latitude, longitude, rayon=500):
    overpass_query = f"""
[out:json][timeout:15];
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
        timeout=20
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


def safe_call(nom, fonction, *args):
    """
    Exécute une fonction en évitant qu'une erreur API bloque toute l'analyse.
    """
    try:
        return fonction(*args)
    except requests.exceptions.Timeout:
        return {
            "erreur": True,
            "message": f"Timeout lors de l'appel du module {nom}.",
            "source": nom
        }
    except requests.exceptions.HTTPError as e:
        return {
            "erreur": True,
            "message": f"Erreur HTTP lors de l'appel du module {nom}.",
            "details": str(e),
            "source": nom
        }
    except requests.exceptions.RequestException as e:
        return {
            "erreur": True,
            "message": f"Erreur réseau lors de l'appel du module {nom}.",
            "details": str(e),
            "source": nom
        }
    except Exception as e:
        return {
            "erreur": True,
            "message": f"Erreur inattendue dans le module {nom}.",
            "details": str(e),
            "source": nom
        }


try:
    localisation = geocoder(adresse)

    if localisation is None:
        print(json.dumps({"error": "Adresse introuvable"}, ensure_ascii=False, indent=2))
        sys.exit(1)

    latitude = localisation["latitude"]
    longitude = localisation["longitude"]
    code_commune = localisation["code_commune"]

    output = {
        "requete": adresse,
        "localisation": localisation,
        "meteo": safe_call("meteo_urgence", meteo, latitude, longitude),
        "risques": safe_call("risques_site", risques, code_commune),
        "equipements_sensibles": safe_call(
            "equipements_sensibles",
            equipements_sensibles,
            latitude,
            longitude,
            500
        )
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))

except requests.RequestException as e:
    print(json.dumps({
        "error": "Erreur lors de la localisation de l'adresse",
        "details": str(e)
    }, ensure_ascii=False, indent=2))
    sys.exit(1)

except Exception as e:
    print(json.dumps({
        "error": "Erreur inattendue lors de l'analyse de zone",
        "details": str(e)
    }, ensure_ascii=False, indent=2))
    sys.exit(1)