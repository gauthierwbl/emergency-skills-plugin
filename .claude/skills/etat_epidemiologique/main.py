import argparse
import json
import requests
import sys

INDICATEURS_URGENCE = {
    "3": "Syndromes Grippaux",
    "84": "COVID-19",
    "114": "Infection Respiratoire Aiguë (IRA)",
    "116": "Diarrhée aiguë (Gastro-entérite)",
    "103": "Varicelle",
    "109": "Maladie de Lyme"
}

def resolve_region_code(location_code: str) -> str:
    if location_code.lower() in ["fr", "france"]:
        return "FR"
    
    if len(location_code) <= 2 and location_code.isdigit():
        return location_code.zfill(2)
        
    url_insee = f"https://geo.api.gouv.fr/communes/{location_code}?fields=codeRegion"
    try:
        response = requests.get(url_insee, timeout=5)
        if response.status_code == 200:
            return response.json().get("codeRegion", "FR")
    except requests.RequestException:
        pass

    url_postal = f"https://geo.api.gouv.fr/communes?codePostal={location_code}&fields=codeRegion"
    try:
        response = requests.get(url_postal, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data:
                return data[0].get("codeRegion", "FR")
    except requests.RequestException:
        pass
    
    return "INVALIDE"

def fetch_regional_epidemiological_data(location_code: str) -> dict:
    region_code = resolve_region_code(location_code)
    
    if region_code == "INVALIDE":
        return {"error": f"Code postal ou INSEE invalide/introuvable : {location_code}"}

    geo_level = "PAY" if region_code == "FR" else "REG"
    api_url = "https://www.sentiweb.fr/api/v1/datasets/rest/incidence"
    alerts = []

    for indicator_id, disease_name in INDICATEURS_URGENCE.items():
        params = {"indicator": indicator_id, "geo": geo_level, "span": "last"}
        if geo_level == "REG":
            params["geo_id"] = region_code

        try:
            response = requests.get(api_url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json().get("data", [])
                if data:
                    record = data[0]
                    alerts.append({
                        "maladie": disease_name,
                        "semaine": record.get("week"),
                        "cas_estimes": record.get("inc", 0),
                        "taux_100k": record.get("inc100", 0)
                    })
        except requests.RequestException:
            continue

    return {
        "zone_evaluee": {"niveau": geo_level, "code_region": region_code},
        "alertes": alerts
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--code_insee", default="FR")
    args = parser.parse_args()
    
    report = fetch_regional_epidemiological_data(args.code_insee)
    print(json.dumps(report, ensure_ascii=False, indent=2))