import requests
import sys
import json

adresse = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""

if not adresse:
    print(json.dumps({"error": "Aucune adresse fournie"}, ensure_ascii=False, indent=2))
    sys.exit(1)

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

try:
    localisation = geocoder(adresse)

    if localisation is None:
        print(json.dumps({"error": "Adresse introuvable"}, ensure_ascii=False, indent=2))
        sys.exit(1)

    meteo_actuelle = meteo(localisation["latitude"], localisation["longitude"])
    risques_commune = risques(localisation["code_commune"])

    output = {
        "requete": adresse,
        "localisation": localisation,
        "meteo": meteo_actuelle,
        "risques": risques_commune
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))

except requests.RequestException as e:
    print(json.dumps({
        "error": "Erreur lors de l'appel à une API externe",
        "details": str(e)
    }, ensure_ascii=False, indent=2))
    sys.exit(1)