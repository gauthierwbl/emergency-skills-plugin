import requests
import sys
import json

code_insee = sys.argv[1] if len(sys.argv) > 1 else ""

if not code_insee:
    print(json.dumps({"error": "Aucun code INSEE fourni"}, ensure_ascii=False, indent=2))
    sys.exit(1)

url = "https://www.georisques.gouv.fr/api/v1/gaspar/risques"
params = {
    "code_insee": code_insee
}

try:
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
except requests.RequestException as e:
    print(json.dumps({
        "error": "Erreur lors de l'appel à l'API Géorisques",
        "details": str(e)
    }, ensure_ascii=False, indent=2))
    sys.exit(1)

if data.get("results", 0) == 0:
    output = {
        "code_insee": code_insee,
        "message": "Aucun risque trouvé pour cette commune avec cet endpoint.",
        "api": "Géorisques",
        "endpoint": "gaspar/risques"
    }
else:
    output = {
        "code_insee": code_insee,
        "api": "Géorisques",
        "endpoint": "gaspar/risques",
        "nombre_resultats": data.get("results"),
        "donnees": data.get("data", [])
    }

print(json.dumps(output, ensure_ascii=False, indent=2))