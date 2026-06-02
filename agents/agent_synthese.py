import json
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def get_client():
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY manquante dans le fichier .env")
    return genai.Client(api_key=GEMINI_API_KEY)


def synthese_locale(demande: str, collecte: dict, analyse: dict) -> str:
    donnees = collecte.get("donnees_collectees", {})

    lignes = [
        "Synthèse locale de secours",
        "",
        f"Demande : {demande}",
        f"Niveau de vigilance : {analyse.get('niveau_vigilance')}",
        "",
        "Démarche recommandée :"
    ]

    for etape in analyse.get("demarche_recommandee", []):
        lignes.append(f"- {etape}")

    localisation = donnees.get("localisation", {})
    meteo = donnees.get("meteo", {})
    equipements = donnees.get("equipements_sensibles", {})

    lignes.append("")
    lignes.append("Informations principales :")
    lignes.append(f"- Adresse : {localisation.get('adresse_trouvee')}")
    lignes.append(f"- Commune : {localisation.get('commune')}")
    lignes.append(f"- Température : {meteo.get('temperature')} °C")
    lignes.append(f"- Vent : {meteo.get('vent_km_h')} km/h")
    lignes.append(f"- Équipements trouvés : {equipements.get('nombre_equipements')}")

    return "\n".join(lignes)


def generer_synthese(demande: str, collecte: dict, analyse: dict) -> str:
    client = get_client()

    prompt = f"""
Tu es un agent de synthèse pour un système d'aide à la décision en situation d'urgence.

Demande utilisateur :
{demande}

Données collectées :
{json.dumps(collecte, ensure_ascii=False, indent=2)}

Analyse produite par l'agent d'analyse :
{json.dumps(analyse, ensure_ascii=False, indent=2)}

Rédige une synthèse claire en français avec :
1. résumé de la situation ;
2. localisation ;
3. météo ;
4. risques et points sensibles ;
5. niveau de vigilance ;
6. meilleure démarche à suivre.

Sois clair, opérationnel et prudent.
Précise que les données doivent être confirmées avec les sources officielles.
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
            + synthese_locale(demande, collecte, analyse)
        )