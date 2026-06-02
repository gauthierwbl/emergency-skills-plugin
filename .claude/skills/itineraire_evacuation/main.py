import argparse
import json
import os
import sys
import webbrowser
import requests

def geocode_destination(adresse: str):
    url = "https://api-adresse.data.gouv.fr/search/"
    try:
        response = requests.get(url, params={"q": adresse, "limit": 1}, timeout=10)
        if response.status_code == 200 and response.json().get("features"):
            feature = response.json()["features"][0]
            lon, lat = feature["geometry"]["coordinates"]
            return lat, lon, feature["properties"].get("label")
    except requests.RequestException:
        pass
    return None

def calculer_evacuation_brouter(lat_depart, lon_depart, lat_dest, lon_dest, danger_lat, danger_lon, danger_rayon):
    """Calcule un itinéraire routier en évitant strictement un périmètre circulaire (nogos)"""
    url = "https://brouter.de/brouter"
    
    params = {
        "lonlats": f"{lon_depart},{lat_depart};{lon_dest},{lat_dest}",
        "profile": "car-fast",
        "format": "geojson"
    }
    
    if danger_lat and danger_lon and danger_rayon:
        params["nogos"] = f"{danger_lon},{danger_lat},{danger_rayon}"
        
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get("features"):
                properties = data["features"][0]["properties"]
                coords = data["features"][0]["geometry"]["coordinates"]
                return {
                    "distance_km": round(float(properties.get("track-length", 0)) / 1000, 2),
                    "duree_min": round(float(properties.get("total-time", 0)) / 60),
                    "coords": coords
                }
    except requests.RequestException:
        pass
    return None

def exporter_carte_leaflet(lat1, lon1, lat2, lon2, trace, danger_lat, danger_lon, danger_rayon):
    """Génère un fichier HTML affichant le départ, l'arrivée, la route et la zone de danger"""
    
    cercle_js = ""
    if danger_lat and danger_lon and danger_rayon:
        cercle_js = f"""
        var dangerCircle = L.circle([{danger_lat}, {danger_lon}], {{
            color: 'red',
            fillColor: '#f03',
            fillOpacity: 0.3,
            radius: {danger_rayon}
        }}).addTo(map).bindPopup('<b>Zone de Danger</b><br>Rayon: {danger_rayon}m');
        """

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Plan d'Évacuation d'Urgence</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body, html, #map {{ height: 100%; margin: 0; padding: 0; font-family: sans-serif; }}
        #banner {{ position: absolute; top: 10px; left: 50px; z-index: 1000; background: #d32f2f; color: white; padding: 10px 20px; font-weight: bold; border-radius: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.5); text-transform: uppercase; }}
    </style>
</head>
<body>
    <div id="banner">Itinéraire d'Évacuation - Évitement Actif</div>
    <div id="map"></div>
    <script>
        var map = L.map('map').setView([{lat1}, {lon1}], 12);
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '© OpenStreetMap contributors'
        }}).addTo(map);

        L.marker([{lat1}, {lon1}]).addTo(map).bindPopup('<b>Position Actuelle</b>').openPopup();
        L.marker([{lat2}, {lon2}]).addTo(map).bindPopup('<b>Point de Repli</b>');

        {cercle_js}

        // BRouter retourne du GeoJSON [lon, lat], Leaflet attend du [lat, lon]
        var polylinePoints = {json.dumps([[c[1], c[0]] for c in trace])};
        var polyline = L.polyline(polylinePoints, {{color: '#1976D2', weight: 5, opacity: 0.9}}).addTo(map);
        
        // Ajuster le zoom pour tout voir
        var group = new L.featureGroup([polyline]);
        if (typeof dangerCircle !== 'undefined') {{ group.addLayer(dangerCircle); }}
        map.fitBounds(group.getBounds().pad(0.1));
    </script>
</body>
</html>"""
    
    output_path = "itineraire_evacuation.html"
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(html_content)
    
    webbrowser.open(f"file://{os.path.abspath(output_path)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--lat", type=float, required=True, help="Latitude de départ")
    parser.add_argument("--lon", type=float, required=True, help="Longitude de départ")
    parser.add_argument("--destination", required=True, help="Adresse ou ville refuge")
    parser.add_argument("--danger_lat", type=float, default=None, help="Latitude de la menace")
    parser.add_argument("--danger_lon", type=float, default=None, help="Longitude de la menace")
    parser.add_argument("--danger_rayon", type=int, default=1000, help="Rayon de la zone à éviter (en mètres)")
    args = parser.parse_args()

    dest_info = geocode_destination(args.destination)
    if not dest_info:
        print(json.dumps({"error": "Destination introuvable via l'API de géocodage"}, ensure_ascii=False))
        sys.exit(1)

    dest_lat, dest_lon, dest_label = dest_info
    
    route = calculer_evacuation_brouter(
        args.lat, args.lon, 
        dest_lat, dest_lon, 
        args.danger_lat, args.danger_lon, args.danger_rayon
    )

    if not route:
        print(json.dumps({"error": "Impossible de calculer un itinéraire évitant la zone de danger spécifiée."}, ensure_ascii=False))
        sys.exit(1)

    exporter_carte_leaflet(
        args.lat, args.lon, 
        dest_lat, dest_lon, 
        route["coords"], 
        args.danger_lat, args.danger_lon, args.danger_rayon
    )

    resume = {
        "statut": "itineraire_securise_calcule",
        "distance_km": route["distance_km"],
        "duree_estimee_minutes": route["duree_min"],
        "contournement_actif": bool(args.danger_lat),
        "fichier_carte": "itineraire_evacuation.html"
    }
    print(json.dumps(resume, ensure_ascii=False, indent=2))