import requests
import sys
import json

query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""

if not query:
    print(json.dumps({"error": "Aucune adresse fournie"}, ensure_ascii=False, indent=2))
    sys.exit(1)

url = "https://api-adresse.data.gouv.fr/search/"
params = {
    "q": query,
    "limit": 1
}

response = requests.get(url, params=params, timeout=10)
response.raise_for_status()
data = response.json()

if not data.get("features"):
    print(json.dumps({"error": "Adresse introuvable"}, ensure_ascii=False, indent=2))
    sys.exit(1)

feature = data["features"][0]
props = feature["properties"]
longitude, latitude = feature["geometry"]["coordinates"]

output = {
    "requete": query,
    "adresse_trouvee": props.get("label"),
    "commune": props.get("city"),
    "code_postal": props.get("postcode"),
    "code_commune": props.get("citycode"),
    "latitude": latitude,
    "longitude": longitude,
    "score": props.get("score"),
    "type": props.get("type")
}

print(json.dumps(output, ensure_ascii=False, indent=2))