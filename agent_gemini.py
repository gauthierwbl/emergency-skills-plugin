import json
import os
import re

from dotenv import load_dotenv
from google import genai

from agents.agent_collecte import collecter_donnees
from agents.agent_analyse import analyser_situation
from agents.agent_synthese import generer_synthese

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def get_client():
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY manquante dans le fichier .env")
    return genai.Client(api_key=GEMINI_API_KEY)


def extraire_json(texte: str) -> dict:
    match = re.search(r"\{.*\}", texte, re.DOTALL)

    if not match:
        return {
            "adresse": texte
        }

    return json.loads(match.group(0))


def extraire_adresse(demande: str) -> str:
    client = get_client()

    prompt = f"""
Tu es un extracteur d'adresse pour un système d'analyse d'urgence.

À partir de la demande utilisateur, retourne uniquement un JSON valide.

Format obligatoire :
{{
  "adresse": "adresse ou lieu à analyser"
}}

Demande utilisateur :
{demande}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        resultat = extraire_json(response.text)
        return resultat.get("adresse", demande)

    except Exception:
        return demande


def main():
    print("Emergency Skills Plugin - Agent Gemini multi-agents")
    print()
    print("Exemple :")
    print("Analyse complète de 12 rue de la Paix Paris")
    print()

    demande = input("Demande utilisateur : ").strip()

    adresse = extraire_adresse(demande)

    print("\n=== Adresse détectée ===")
    print(adresse)

    print("\n=== Agent de collecte ===")
    collecte = collecter_donnees(adresse)
    print(json.dumps(collecte, ensure_ascii=False, indent=2))

    print("\n=== Agent d'analyse ===")
    analyse = analyser_situation(collecte)
    print(json.dumps(analyse, ensure_ascii=False, indent=2))

    print("\n=== Agent de synthèse ===")
    synthese = generer_synthese(demande, collecte, analyse)
    print(synthese)


if __name__ == "__main__":
    main()