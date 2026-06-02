import json
import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from google import genai

load_dotenv()

BASE_DIR = Path(__file__).parent
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


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


def analyser_zone(adresse: str) -> dict:
    return run_script(
        ".claude/skills/analyse_zone/main.py",
        [adresse]
    )


def generer_synthese(donnees: dict) -> str:
    if not GEMINI_API_KEY:
        return "Erreur : GEMINI_API_KEY manquante dans le fichier .env"

    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = f"""
Tu es un agent d'aide à la décision en situation d'urgence.

À partir des données JSON suivantes, produis une synthèse claire en français.

Structure attendue :
1. Localisation
2. Conditions météo
3. Risques identifiés
4. Équipements sensibles proches
5. Niveau de vigilance : faible, modéré ou élevé
6. Recommandations opérationnelles

Données :
{json.dumps(donnees, ensure_ascii=False, indent=2)}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


def main():
    print("Agent Gemini - Emergency Skills Plugin")
    print("Exemple : 12 rue de la paix Paris")
    print()

    adresse = input("Adresse à analyser : ").strip()

    donnees = analyser_zone(adresse)

    print("\n=== Données collectées ===")
    print(json.dumps(donnees, ensure_ascii=False, indent=2))

    print("\n=== Synthèse Gemini ===")
    synthese = generer_synthese(donnees)
    print(synthese)


if __name__ == "__main__":
    main()