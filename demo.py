"""
Fichier de démonstration du projet Emergency Skills Plugin.

Ce script permet de lancer rapidement une analyse de zone
à partir d'une adresse d'exemple.
"""

import json
import subprocess
import sys
from pathlib import Path


def run_analyse_zone(adresse: str):
    """
    Lance le skill analyse_zone avec une adresse donnée.
    """

    script_path = Path(".claude") / "skills" / "analyse_zone" / "main.py"

    if not script_path.exists():
        return {
            "erreur": True,
            "message": f"Le fichier {script_path} est introuvable."
        }

    try:
        result = subprocess.run(
            [sys.executable, str(script_path), adresse],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30
        )

        if result.returncode != 0:
            return {
                "erreur": True,
                "message": "Erreur lors de l'exécution du skill analyse_zone.",
                "details": result.stderr
            }

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {
                "erreur": True,
                "message": "La sortie du skill n'est pas un JSON valide.",
                "sortie": result.stdout
            }

    except Exception as e:
        return {
            "erreur": True,
            "message": str(e)
        }


def main():
    """
    Point d'entrée de la démonstration.
    """

    adresse = "12 rue de la Paix Paris"

    print("=== Emergency Skills Plugin ===")
    print("Démonstration d'analyse de zone")
    print()
    print(f"Adresse analysée : {adresse}")
    print()

    resultat = run_analyse_zone(adresse)

    print("Résultat obtenu :")
    print(json.dumps(resultat, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()