import json
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


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


def collecter_donnees(adresse: str) -> dict:
    """
    Agent de collecte.
    Récupère toutes les données nécessaires à partir d'une adresse.
    """

    donnees = run_script(
        ".claude/skills/analyse_zone/main.py",
        [adresse]
    )

    return {
        "adresse_demandee": adresse,
        "donnees_collectees": donnees
    }