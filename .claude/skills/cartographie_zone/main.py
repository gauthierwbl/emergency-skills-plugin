import json
import sys
import subprocess
from pathlib import Path

import folium

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


def run_script(script_path: str, args: list[str]) -> dict:
    command = ["python", str(BASE_DIR / script_path), *args]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    if result.returncode != 0:
        return {
            "error": "Erreur lors de l'exécution du script",
            "details": result.stderr
        }

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {
            "error": "Sortie JSON invalide",
            "stdout": result.stdout
        }


def couleur_par_type(type_equipement: str) -> str:
    couleurs = {
        "pharmacy": "green",
        "school": "blue",
        "hospital": "red",
        "clinic": "red",
        "police": "darkblue",
        "fire_station": "orange",
    }

    return couleurs.get(type_equipement, "gray")


def generer_carte(adresse: str, rayon: int = 500) -> dict:
    analyse = run_script(
        ".claude/skills/analyse_zone/main.py",
        [adresse]
    )

    if "error" in analyse:
        return analyse

    localisation = analyse.get("localisation", {})
    equipements_data = analyse.get("equipements_sensibles", {})

    latitude = localisation.get("latitude")
    longitude = localisation.get("longitude")

    if latitude is None or longitude is None:
        return {
            "error": "Coordonnées GPS introuvables",
            "localisation": localisation
        }

    carte = folium.Map(
        location=[latitude, longitude],
        zoom_start=16
    )

    folium.Marker(
        location=[latitude, longitude],
        popup=f"Zone analysée : {localisation.get('adresse_trouvee')}",
        tooltip="Point central",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(carte)

    folium.Circle(
        location=[latitude, longitude],
        radius=rayon,
        popup=f"Périmètre de {rayon} mètres",
        color="red",
        fill=True,
        fill_opacity=0.08
    ).add_to(carte)

    for equipement in equipements_data.get("equipements", []):
        lat = equipement.get("latitude")
        lon = equipement.get("longitude")
        nom = equipement.get("nom", "Nom non renseigné")
        type_equipement = equipement.get("type", "inconnu")
        distance = equipement.get("distance_m")

        if lat is None or lon is None:
            continue

        folium.Marker(
            location=[lat, lon],
            popup=f"{nom}<br>Type : {type_equipement}<br>Distance : {distance} m",
            tooltip=f"{type_equipement} - {distance} m",
            icon=folium.Icon(
                color=couleur_par_type(type_equipement),
                icon="plus-sign"
            )
        ).add_to(carte)

    nom_fichier = "carte_zone.html"
    chemin_sortie = OUTPUT_DIR / nom_fichier

    carte.save(str(chemin_sortie))

    return {
        "adresse": adresse,
        "adresse_trouvee": localisation.get("adresse_trouvee"),
        "latitude": latitude,
        "longitude": longitude,
        "rayon_m": rayon,
        "nombre_equipements": equipements_data.get("nombre_equipements"),
        "carte_generee": str(chemin_sortie)
    }


def main():
    adresse = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""

    if not adresse:
        print(json.dumps({
            "error": "Aucune adresse fournie",
            "usage": "python main.py \"12 rue de la Paix Paris\""
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    resultat = generer_carte(adresse)
    print(json.dumps(resultat, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()