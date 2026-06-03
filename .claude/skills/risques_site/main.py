import json
import sys
from typing import Any

import requests


GEORISQUES_BASE_URL = "https://www.georisques.gouv.fr/api/v1"


RISQUE_POIDS = {
    "INONDATION": 25,
    "INOND": 25,
    "MVT": 15,
    "MOUVEMENT": 15,
    "SEISME": 20,
    "SISM": 20,
    "RGA": 15,
    "ARGILE": 15,
    "FEU": 10,
    "FEUFOR": 10,
    "AVALANCHE": 10,
    "INDUSTRIEL": 25,
    "ICPE": 25,
    "RUPTURE_BARRAGE": 20,
    "BARRAGE": 20,
    "TMD": 10,
    "RADON": 5,
    "CAVITE": 15,
    "POLLUTION": 20,
}


def appel_api(endpoint: str, params: dict[str, Any]) -> dict:
    url = f"{GEORISQUES_BASE_URL}/{endpoint}"

    try:
        response = requests.get(url, params=params, timeout=15)
        return {
            "endpoint": endpoint,
            "url": response.url,
            "status_code": response.status_code,
            "ok": response.ok,
            "data": response.json() if response.text else None,
        }

    except requests.RequestException as e:
        return {
            "endpoint": endpoint,
            "ok": False,
            "error": str(e),
            "data": None,
        }

    except ValueError:
        return {
            "endpoint": endpoint,
            "ok": False,
            "error": "Réponse non JSON",
            "data": None,
        }


def extraire_liste_resultats(reponse: dict) -> list:
    data = reponse.get("data")

    if data is None:
        return []

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in ["data", "results", "resultats", "features"]:
            value = data.get(key)
            if isinstance(value, list):
                return value

    return []


def normaliser_texte(value: Any) -> str:
    if value is None:
        return ""

    return str(value).upper()


def detecter_risques_depuis_objet(obj: Any) -> list[str]:
    risques = []

    texte = normaliser_texte(obj)

    mots_cles = {
        "inondation": ["INONDATION", "INOND", "CRUE", "SUBMERSION"],
        "mouvement_terrain": ["MOUVEMENT", "MVT", "GLISSEMENT", "EBOULEMENT", "EFFONDREMENT"],
        "seisme": ["SEISME", "SISMIQUE", "SISM"],
        "argiles": ["ARGILE", "RGA", "RETRAIT", "GONFLEMENT"],
        "feu_foret": ["FEU", "FORET", "INCENDIE"],
        "avalanche": ["AVALANCHE"],
        "industriel": ["INDUSTRIEL", "ICPE", "INSTALLATION CLASSEE"],
        "barrage": ["BARRAGE", "RUPTURE"],
        "tmd": ["MATIERES DANGEREUSES", "TMD", "TRANSPORT"],
        "radon": ["RADON"],
        "cavite": ["CAVITE", "SOUTERRAINE"],
        "pollution": ["POLLUTION", "BASOL", "SIS", "SOL POLLUE"],
    }

    for risque, keywords in mots_cles.items():
        if any(keyword in texte for keyword in keywords):
            risques.append(risque)

    return risques


def consolider_risques(reponses: list[dict]) -> dict:
    risques_detectes = {}
    endpoints_ok = []
    endpoints_erreur = []
    donnees_brutes_resume = {}

    for reponse in reponses:
        endpoint = reponse.get("endpoint")

        if reponse.get("ok"):
            endpoints_ok.append(endpoint)
        else:
            endpoints_erreur.append({
                "endpoint": endpoint,
                "error": reponse.get("error"),
                "status_code": reponse.get("status_code"),
            })

        resultats = extraire_liste_resultats(reponse)
        donnees_brutes_resume[endpoint] = {
            "status_code": reponse.get("status_code"),
            "ok": reponse.get("ok"),
            "nombre_resultats": len(resultats),
            "url": reponse.get("url"),
        }

        for item in resultats:
            risques = detecter_risques_depuis_objet(item)

            for risque in risques:
                if risque not in risques_detectes:
                    risques_detectes[risque] = {
                        "occurrences": 0,
                        "sources": set()
                    }

                risques_detectes[risque]["occurrences"] += 1
                risques_detectes[risque]["sources"].add(endpoint)

    risques_liste = []

    for risque, infos in risques_detectes.items():
        risques_liste.append({
            "type": risque,
            "occurrences": infos["occurrences"],
            "sources": sorted(list(infos["sources"]))
        })

    return {
        "risques_detectes": risques_liste,
        "endpoints_ok": endpoints_ok,
        "endpoints_erreur": endpoints_erreur,
        "donnees_brutes_resume": donnees_brutes_resume
    }


def calculer_score_risque(risques_detectes: list[dict], endpoints_erreur: list[dict]) -> dict:
    score = 0
    details = []

    for risque in risques_detectes:
        type_risque = risque.get("type", "").upper()
        occurrences = risque.get("occurrences", 1)

        poids = 10

        for cle, valeur in RISQUE_POIDS.items():
            if cle in type_risque:
                poids = valeur
                break

        bonus_occurrences = min(occurrences * 2, 10)
        contribution = min(poids + bonus_occurrences, 35)

        score += contribution
        details.append(f"{risque.get('type')} : +{contribution}")

    if endpoints_erreur:
        details.append("Certaines sources n'ont pas répondu : niveau de confiance réduit.")

    score = min(score, 100)

    if score >= 70:
        niveau = "élevé"
    elif score >= 35:
        niveau = "modéré"
    elif score > 0:
        niveau = "faible"
    else:
        niveau = "non détecté"

    return {
        "score_risque": score,
        "niveau_risque": niveau,
        "details_score": details
    }


def evaluer_confiance(endpoints_ok: list[str], endpoints_erreur: list[dict], risques_detectes: list[dict]) -> dict:
    score = 50

    score += len(endpoints_ok) * 12
    score -= len(endpoints_erreur) * 15

    if risques_detectes:
        score += 10

    score = max(0, min(score, 100))

    if score >= 75:
        niveau = "bonne"
    elif score >= 45:
        niveau = "moyenne"
    else:
        niveau = "faible"

    return {
        "score_confiance": score,
        "niveau_confiance": niveau
    }


def generer_points_vigilance(risques_detectes: list[dict], niveau_risque: str, confiance: dict) -> list[str]:
    points = []

    types = [r.get("type") for r in risques_detectes]

    if "inondation" in types:
        points.append("Vérifier les zones basses, sous-sols, accès routiers et risques de ruissellement.")

    if "industriel" in types:
        points.append("Contrôler la présence éventuelle d'installations industrielles ou de substances dangereuses.")

    if "mouvement_terrain" in types or "cavite" in types:
        points.append("Prendre en compte la stabilité des sols et la présence possible de cavités ou mouvements de terrain.")

    if "seisme" in types:
        points.append("Consulter les règles parasismiques et les documents officiels de prévention.")

    if "argiles" in types:
        points.append("Le retrait-gonflement des argiles peut affecter les bâtiments et infrastructures.")

    if niveau_risque == "non détecté":
        points.append("Aucun risque exploitable n'a été détecté via les endpoints testés.")

    if confiance.get("niveau_confiance") != "bonne":
        points.append("Les données doivent être confirmées avec Géorisques ou les documents communaux officiels.")

    points.append("L'absence de résultat ne signifie pas absence totale de risque.")

    return points


def analyser_commune(code_insee: str) -> dict:
    endpoints = [
        ("gaspar/risques", {"code_insee": code_insee}),
        ("installations_classees", {"code_insee": code_insee}),
        ("catnat", {"code_insee": code_insee}),
    ]

    reponses = []

    for endpoint, params in endpoints:
        reponses.append(appel_api(endpoint, params))

    consolidation = consolider_risques(reponses)
    score = calculer_score_risque(
        consolidation["risques_detectes"],
        consolidation["endpoints_erreur"]
    )
    confiance = evaluer_confiance(
        consolidation["endpoints_ok"],
        consolidation["endpoints_erreur"],
        consolidation["risques_detectes"]
    )

    points_vigilance = generer_points_vigilance(
        consolidation["risques_detectes"],
        score["niveau_risque"],
        confiance
    )

    return {
        "code_insee": code_insee,
        "source": "Géorisques API v1",
        "resume": {
            "nombre_types_risques_detectes": len(consolidation["risques_detectes"]),
            "niveau_risque": score["niveau_risque"],
            "score_risque": score["score_risque"],
            "niveau_confiance": confiance["niveau_confiance"],
            "score_confiance": confiance["score_confiance"],
        },
        "risques_detectes": consolidation["risques_detectes"],
        "score": score,
        "confiance": confiance,
        "points_vigilance": points_vigilance,
        "endpoints": {
            "ok": consolidation["endpoints_ok"],
            "erreurs": consolidation["endpoints_erreur"]
        },
        "donnees_brutes_resume": consolidation["donnees_brutes_resume"],
        "limites": [
            "Les APIs publiques peuvent retourner des données incomplètes ou indisponibles.",
            "Certains endpoints Géorisques peuvent évoluer ou être temporairement indisponibles.",
            "Les résultats doivent être confirmés avec les documents officiels : DICRIM, PPR, DDRM, Géorisques.",
            "L'absence de résultat ne garantit pas l'absence de risque."
        ]
    }


def main():
    code_insee = sys.argv[1] if len(sys.argv) > 1 else ""

    if not code_insee:
        print(json.dumps({
            "error": "Aucun code INSEE fourni",
            "usage": "python main.py <code_insee>"
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    resultat = analyser_commune(code_insee)
    print(json.dumps(resultat, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()