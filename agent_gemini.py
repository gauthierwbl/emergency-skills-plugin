import json
import os
import re
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from google import genai

load_dotenv()

BASE_DIR = Path(__file__).parent
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def get_client():
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY manquante dans le fichier .env")
    return genai.Client(api_key=GEMINI_API_KEY)


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


def extraire_json(texte: str) -> dict:
    match = re.search(r"\{.*\}", texte, re.DOTALL)
    if not match:
        return {
            "intent": "analyse_complete",
            "adresse": texte
        }

    return json.loads(match.group(0))


def comprendre_demande(demande: str) -> dict:
    client = get_client()

    prompt = f"""
Tu es un routeur d'intentions pour un système d'analyse d'urgence.

Analyse la demande utilisateur et retourne uniquement un JSON valide.

Intentions possibles :
- "analyse_complete" : analyse complète d'une zone
- "localisation" : seulement localiser une adresse
- "meteo" : seulement obtenir la météo
- "risques" : seulement obtenir les risques
- "equipements" : seulement obtenir les équipements sensibles proches

Format obligatoire :
{{
  "intent": "...",
  "adresse": "adresse ou lieu extrait de la demande"
}}

Demande utilisateur :
{demande}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return extraire_json(response.text)


def localiser(adresse: str) -> dict:
    return run_script(
        ".claude/skills/localisation_site/main.py",
        [adresse]
    )


def meteo_ville(adresse: str) -> dict:
    return run_script(
        ".claude/skills/meteo_urgence/main.py",
        [adresse]
    )


def risques(code_insee: str) -> dict:
    return run_script(
        ".claude/skills/risques_site/main.py",
        [code_insee]
    )


def equipements(latitude: float, longitude: float, rayon: int = 500) -> dict:
    return run_script(
        ".claude/skills/equipements_sensibles/main.py",
        [str(latitude), str(longitude), str(rayon)]
    )


def analyse_complete(adresse: str) -> dict:
    return run_script(
        ".claude/skills/analyse_zone/main.py",
        [adresse]
    )


def executer_workflow(intent: str, adresse: str) -> dict:
    if intent == "analyse_complete":
        return analyse_complete(adresse)

    if intent == "localisation":
        return {
            "localisation": localiser(adresse)
        }

    if intent == "meteo":
        return {
            "meteo": meteo_ville(adresse)
        }

    localisation = localiser(adresse)

    if intent == "risques":
        return {
            "localisation": localisation,
            "risques": risques(localisation.get("code_commune", ""))
        }

    if intent == "equipements":
        return {
            "localisation": localisation,
            "equipements_sensibles": equipements(
                localisation.get("latitude"),
                localisation.get("longitude"),
                500
            )
        }

    return analyse_complete(adresse)

def reduire_donnees_pour_synthese(donnees: dict) -> dict:
    donnees_reduites = dict(donnees)

    equipements = donnees_reduites.get("equipements_sensibles", {})

    if isinstance(equipements, dict) and "equipements" in equipements:
        equipements["equipements"] = equipements["equipements"][:5]
        donnees_reduites["equipements_sensibles"] = equipements

    return donnees_reduites

def synthese_locale(demande: str, routage: dict, donnees: dict) -> str:
    lignes = []

    lignes.append("Synthèse locale de secours")
    lignes.append("")
    lignes.append(f"Demande : {demande}")
    lignes.append(f"Intention détectée : {routage.get('intent')}")
    lignes.append("")

    localisation = donnees.get("localisation", {})
    meteo = donnees.get("meteo", {})
    risques_data = donnees.get("risques", {})
    equipements_data = donnees.get("equipements_sensibles", {})

    if localisation:
        lignes.append("Localisation :")
        lignes.append(f"- Adresse : {localisation.get('adresse_trouvee')}")
        lignes.append(f"- Commune : {localisation.get('commune')}")
        lignes.append(f"- Coordonnées : {localisation.get('latitude')}, {localisation.get('longitude')}")
        lignes.append("")

    if meteo:
        lignes.append("Météo :")
        lignes.append(f"- Température : {meteo.get('temperature')} °C")
        lignes.append(f"- Vent : {meteo.get('vent_km_h')} km/h")
        lignes.append(f"- Pluie : {meteo.get('pluie_mm')} mm")
        lignes.append("")

    if risques_data:
        lignes.append("Risques :")
        lignes.append(f"- {risques_data.get('message', 'Données disponibles')}")
        lignes.append("")

    if equipements_data:
        lignes.append("Équipements sensibles :")
        lignes.append(f"- Nombre trouvé : {equipements_data.get('nombre_equipements')}")

        for equipement in equipements_data.get("equipements", [])[:5]:
            lignes.append(
                f"- {equipement.get('nom')} ({equipement.get('type')}) à {equipement.get('distance_m')} m"
            )

        lignes.append("")

    lignes.append("Niveau de vigilance : à confirmer selon les données disponibles.")
    lignes.append("Recommandation : vérifier les informations avec les sources officielles avant toute décision opérationnelle.")

    return "\n".join(lignes)

def generer_synthese(demande: str, routage: dict, donnees: dict) -> str:
    client = get_client()

    prompt = f"""
Tu es un agent d'aide à la décision en situation d'urgence.

Demande utilisateur :
{demande}

Intention détectée :
{json.dumps(routage, ensure_ascii=False, indent=2)}

Données collectées :
{json.dumps(reduire_donnees_pour_synthese(donnees), ensure_ascii=False, indent=2)}

Réponds en français avec une synthèse claire, courte et utile.
Si les données sont insuffisantes, indique-le clairement.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:
        return (
            "Gemini est temporairement indisponible.\n"
            f"Détail technique : {e}\n\n"
            + synthese_locale(demande, routage, donnees)
        )


def main():
    print("Agent Gemini - mode langage naturel")
    print("Exemples :")
    print("- Analyse complète de 12 rue de la Paix Paris")
    print("- Donne-moi les équipements autour de 12 rue de la Paix Paris")
    print("- Quelle est la météo à Belfort ?")
    print("- Quels sont les risques à 12 rue de la Paix Paris ?")
    print()

    demande = input("Demande utilisateur : ").strip()

    routage = comprendre_demande(demande)
    intent = routage.get("intent", "analyse_complete")
    adresse = routage.get("adresse", demande)

    donnees = executer_workflow(intent, adresse)

    print("\n=== Routage Gemini ===")
    print(json.dumps(routage, ensure_ascii=False, indent=2))

    print("\n=== Données collectées ===")
    print(json.dumps(donnees, ensure_ascii=False, indent=2))

    print("\n=== Synthèse Gemini ===")
    print(generer_synthese(demande, routage, donnees))


if __name__ == "__main__":
    main()