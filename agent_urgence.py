import json
import subprocess
from pathlib import Path

from langchain_core.tools import tool

BASE_DIR = Path(__file__).parent


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

    if not result.stdout:
        return {
            "error": "Aucune sortie retournée par le script"
        }

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {
            "error": "Sortie JSON invalide",
            "stdout": result.stdout
        }


@tool
def analyser_zone(adresse: str) -> dict:
    """Analyse une adresse en situation d'urgence : localisation, météo, risques et équipements sensibles."""
    return run_script(
        ".claude/skills/analyse_zone/main.py",
        [adresse]
    )


@tool
def localiser_site(adresse: str) -> dict:
    """Convertit une adresse française en coordonnées GPS, commune, code postal et code INSEE."""
    return run_script(
        ".claude/skills/localisation_site/main.py",
        [adresse]
    )


@tool
def rechercher_equipements(latitude: float, longitude: float, rayon: int = 500) -> dict:
    """Recherche les équipements sensibles autour de coordonnées GPS : écoles, pharmacies, hôpitaux, police, pompiers."""
    return run_script(
        ".claude/skills/equipements_sensibles/main.py",
        [str(latitude), str(longitude), str(rayon)]
    )


def main():
    print("Agent urgence - démonstration")
    print("Exemple : Analyse la zone 12 rue de la paix Paris")
    print()

    question = input("Demande utilisateur : ")

    # Version MVP sans clé API : on appelle directement l'outil principal.
    resultat = analyser_zone.invoke({"adresse": question.replace("Analyse la zone", "").strip()})

    print("\n=== Résultat brut JSON ===")
    print(json.dumps(resultat, ensure_ascii=False, indent=2))

    print("\n=== Synthèse opérationnelle ===")

    localisation = resultat.get("localisation", {})
    meteo = resultat.get("meteo", {})
    risques = resultat.get("risques", {})
    equipements = resultat.get("equipements_sensibles", {})

    print(f"Adresse trouvée : {localisation.get('adresse_trouvee')}")
    print(f"Commune : {localisation.get('commune')} ({localisation.get('code_commune')})")
    print(f"Coordonnées : {localisation.get('latitude')}, {localisation.get('longitude')}")
    print(f"Météo : {meteo.get('temperature')}°C, vent {meteo.get('vent_km_h')} km/h")
    print(f"Pluie : {meteo.get('pluie_mm')} mm")
    print(f"Risques : {risques.get('message', 'Données disponibles')}")
    print(f"Équipements sensibles trouvés : {equipements.get('nombre_equipements')}")

    for e in equipements.get("equipements", [])[:5]:
        print(f"- {e.get('nom')} ({e.get('type')}) à {e.get('distance_m')} m")


if __name__ == "__main__":
    main()