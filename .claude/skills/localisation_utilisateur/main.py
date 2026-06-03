import json
import requests

def get_user_location():
    try:
        ip_resp = requests.get("https://ipinfo.io/json", timeout=5)
        ip_resp.raise_for_status()
        ip_data = ip_resp.json()
        
        loc = ip_data.get("loc", "")
        if not loc:
            return {"error": "coordonnees_introuvables"}
            
        lat, lon = loc.split(",")
        
        geo_resp = requests.get(f"https://api-adresse.data.gouv.fr/reverse/?lon={lon}&lat={lat}", timeout=5)
        geo_resp.raise_for_status()
        geo_data = geo_resp.json()
        
        code_insee = None
        if geo_data.get("features"):
            code_insee = geo_data["features"][0]["properties"].get("citycode")
            
        return {
            "latitude": float(lat),
            "longitude": float(lon),
            "ville": ip_data.get("city"),
            "code_insee": code_insee
        }
    except requests.RequestException:
        return {"error": "erreur_reseau"}
    except ValueError:
        return {"error": "donnees_invalides"}

if __name__ == "__main__":
    print(json.dumps(get_user_location(), ensure_ascii=False, indent=2))