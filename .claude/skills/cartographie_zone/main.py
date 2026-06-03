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


def style_equipement(type_equipement: str) -> dict:
    styles = {
        "pharmacy": {
            "couleur": "green",
            "icone": "plus-sign",
            "priorite": "utile"
        },
        "school": {
            "couleur": "blue",
            "icone": "education",
            "priorite": "sensible"
        },
        "hospital": {
            "couleur": "red",
            "icone": "plus-sign",
            "priorite": "critique"
        },
        "clinic": {
            "couleur": "red",
            "icone": "plus-sign",
            "priorite": "critique"
        },
        "police": {
            "couleur": "darkblue",
            "icone": "info-sign",
            "priorite": "secours"
        },
        "fire_station": {
            "couleur": "orange",
            "icone": "fire",
            "priorite": "secours"
        },
    }

    return styles.get(type_equipement, {
        "couleur": "gray",
        "icone": "info-sign",
        "priorite": "inconnu"
    })


def couleur_distance(distance: int | None) -> str:
    if distance is None:
        return "gray"

    if distance <= 150:
        return "red"

    if distance <= 300:
        return "orange"

    return "green"


def ajouter_legende(carte: folium.Map):
    legende = """
    <div style="
        position: fixed;
        bottom: 40px;
        left: 40px;
        z-index: 9999;
        background-color: white;
        padding: 12px;
        border: 2px solid #444;
        border-radius: 8px;
        font-size: 14px;
        box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
    ">
        <b>Légende - Cartographie intelligente</b><br><br>
        <span style="color:red;">●</span> Zone proche ou critique<br>
        <span style="color:orange;">●</span> Zone de vigilance<br>
        <span style="color:green;">●</span> Équipement utile éloigné<br>
        <span style="color:blue;">●</span> École / établissement sensible<br>
        <span style="color:darkblue;">●</span> Police<br>
        <span style="color:red;">●</span> Hôpital / clinique<br>
        <br>
        Cercle rouge : périmètre 500 m<br>
        Cercle orange : vigilance 250 m
    </div>
    """

    carte.get_root().html.add_child(folium.Element(legende))


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
        zoom_start=16,
        tiles="OpenStreetMap"
    )

    folium.Marker(
        location=[latitude, longitude],
        popup=(
            f"<b>Zone d'intervention</b><br>"
            f"{localisation.get('adresse_trouvee')}<br>"
            f"Commune : {localisation.get('commune')}<br>"
            f"Code INSEE : {localisation.get('code_commune')}"
        ),
        tooltip="Point central de l'intervention",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(carte)

    folium.Circle(
        location=[latitude, longitude],
        radius=rayon,
        popup=f"Périmètre principal : {rayon} mètres",
        color="red",
        fill=True,
        fill_opacity=0.06
    ).add_to(carte)

    folium.Circle(
        location=[latitude, longitude],
        radius=250,
        popup="Zone de vigilance rapprochée : 250 mètres",
        color="orange",
        fill=True,
        fill_opacity=0.10
    ).add_to(carte)

    equipements_critiques = []
    equipements_sensibles = []
    equipements_utiles = []

    for equipement in equipements_data.get("equipements", []):
        lat = equipement.get("latitude")
        lon = equipement.get("longitude")
        nom = equipement.get("nom", "Nom non renseigné")
        type_equipement = equipement.get("type", "inconnu")
        distance = equipement.get("distance_m")

        if lat is None or lon is None:
            continue

        style = style_equipement(type_equipement)
        couleur = couleur_distance(distance)

        if style["priorite"] == "critique" or (distance is not None and distance <= 150):
            equipements_critiques.append(equipement)
        elif style["priorite"] == "sensible":
            equipements_sensibles.append(equipement)
        else:
            equipements_utiles.append(equipement)

        popup = (
            f"<b>{nom}</b><br>"
            f"Type : {type_equipement}<br>"
            f"Priorité : {style['priorite']}<br>"
            f"Distance : {distance} m"
        )

        folium.Marker(
            location=[lat, lon],
            popup=popup,
            tooltip=f"{type_equipement} - {distance} m",
            icon=folium.Icon(
                color=couleur,
                icon=style["icone"]
            )
        ).add_to(carte)

    ajouter_legende(carte)

    nom_fichier = "carte_zone_intelligente.html"
    chemin_sortie = OUTPUT_DIR / nom_fichier

    carte.save(str(chemin_sortie))

    return {
        "adresse": adresse,
        "adresse_trouvee": localisation.get("adresse_trouvee"),
        "latitude": latitude,
        "longitude": longitude,
        "rayon_m": rayon,
        "nombre_equipements": equipements_data.get("nombre_equipements"),
        "equipements_critiques": len(equipements_critiques),
        "equipements_sensibles": len(equipements_sensibles),
        "equipements_utiles": len(equipements_utiles),
        "carte_generee": str(chemin_sortie),
        "description": "Carte intelligente avec périmètre, zone de vigilance, équipements classés et légende."
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