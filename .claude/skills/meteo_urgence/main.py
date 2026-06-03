import json
import sys
from datetime import datetime, timedelta

import requests


def is_float(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def niveau_depuis_score(score: int) -> str:
    if score >= 80:
        return "critique"
    if score >= 60:
        return "élevé"
    if score >= 30:
        return "modéré"
    return "faible"


def decoder_weather_code(code):
    codes = {
        0: "Ciel dégagé",
        1: "Principalement clair",
        2: "Partiellement nuageux",
        3: "Couvert",
        45: "Brouillard",
        48: "Brouillard givrant",
        51: "Bruine faible",
        53: "Bruine modérée",
        55: "Bruine dense",
        56: "Bruine verglaçante faible",
        57: "Bruine verglaçante dense",
        61: "Pluie faible",
        63: "Pluie modérée",
        65: "Pluie forte",
        66: "Pluie verglaçante faible",
        67: "Pluie verglaçante forte",
        71: "Neige faible",
        73: "Neige modérée",
        75: "Neige forte",
        77: "Grains de neige",
        80: "Averses faibles",
        81: "Averses modérées",
        82: "Averses violentes",
        85: "Averses de neige faibles",
        86: "Averses de neige fortes",
        95: "Orage",
        96: "Orage avec grêle faible",
        99: "Orage avec grêle forte",
    }

    return codes.get(code, "Code météo inconnu")


def analyser_conditions(conditions: dict) -> dict:
    score = 0
    risques = []
    impacts = []
    recommandations = []
    details_score = []

    temperature = conditions.get("temperature_c")
    temperature_ressentie = conditions.get("temperature_ressentie_c")
    humidite = conditions.get("humidite_pct")
    precipitation = conditions.get("precipitation_mm") or 0
    pluie = conditions.get("pluie_mm") or 0
    neige = conditions.get("neige_cm") or 0
    vent = conditions.get("vent_km_h") or 0
    rafales = conditions.get("rafales_km_h") or 0
    visibilite = conditions.get("visibilite_m")
    nuages = conditions.get("nuages_pct")
    weather_code = conditions.get("weather_code")

    pluie_totale = max(precipitation, pluie)

    # Vent moyen
    if vent >= 80:
        score += 30
        risques.append("Vent très fort")
        impacts.append("Déplacements et interventions extérieures fortement perturbés.")
        recommandations.append("Limiter les interventions exposées au vent et sécuriser les objets instables.")
        details_score.append("Vent très fort : +30")
    elif vent >= 60:
        score += 22
        risques.append("Vent fort")
        impacts.append("Risque de gêne pour les interventions extérieures.")
        recommandations.append("Prendre en compte les arbres, toitures, panneaux et objets légers.")
        details_score.append("Vent fort : +22")
    elif vent >= 40:
        score += 12
        risques.append("Vent significatif")
        impacts.append("Intervention extérieure potentiellement moins confortable.")
        recommandations.append("Surveiller les zones exposées au vent.")
        details_score.append("Vent significatif : +12")

    # Rafales
    if rafales >= 100:
        score += 30
        risques.append("Rafales très violentes")
        impacts.append("Risque élevé de chute d'objets, branches ou éléments instables.")
        recommandations.append("Éviter les zones boisées, structures légères et façades exposées.")
        details_score.append("Rafales très violentes : +30")
    elif rafales >= 80:
        score += 20
        risques.append("Rafales importantes")
        impacts.append("Possibilité de danger ponctuel en extérieur.")
        recommandations.append("Renforcer la vigilance sur les accès et les zones dégagées.")
        details_score.append("Rafales importantes : +20")
    elif rafales >= 60:
        score += 10
        risques.append("Rafales modérées à fortes")
        impacts.append("Gêne possible pour les opérations extérieures.")
        recommandations.append("Surveiller les équipements et objets mobiles.")
        details_score.append("Rafales modérées à fortes : +10")

    # Pluie / précipitations
    if pluie_totale >= 20:
        score += 25
        risques.append("Précipitations fortes")
        impacts.append("Risque de ruissellement, chaussées glissantes et accès dégradés.")
        recommandations.append("Vérifier les accès routiers, pentes, sous-sols et zones basses.")
        details_score.append("Précipitations fortes : +25")
    elif pluie_totale >= 10:
        score += 15
        risques.append("Précipitations modérées")
        impacts.append("Circulation et accès potentiellement dégradés.")
        recommandations.append("Prévoir des temps de déplacement plus longs.")
        details_score.append("Précipitations modérées : +15")
    elif pluie_totale > 0:
        score += 5
        risques.append("Présence de pluie")
        impacts.append("Sols potentiellement humides ou glissants.")
        recommandations.append("Vérifier l'état des accès piétons et routiers.")
        details_score.append("Présence de pluie : +5")

    # Neige
    if neige >= 5:
        score += 25
        risques.append("Chutes de neige importantes")
        impacts.append("Accès et déplacements fortement perturbés.")
        recommandations.append("Prévoir équipements adaptés et vérifier les accès routiers.")
        details_score.append("Neige importante : +25")
    elif neige > 0:
        score += 10
        risques.append("Présence de neige")
        impacts.append("Sol potentiellement glissant.")
        recommandations.append("Adapter les déplacements et vérifier les accès.")
        details_score.append("Présence de neige : +10")

    # Visibilité
    if visibilite is not None:
        if visibilite < 1000:
            score += 20
            risques.append("Visibilité très réduite")
            impacts.append("Repérage, conduite et intervention rendus difficiles.")
            recommandations.append("Renforcer le balisage et limiter les déplacements non indispensables.")
            details_score.append("Visibilité très réduite : +20")
        elif visibilite < 5000:
            score += 10
            risques.append("Visibilité réduite")
            impacts.append("Conduite et repérage potentiellement gênés.")
            recommandations.append("Adapter la vitesse d'approche et prévoir un repérage renforcé.")
            details_score.append("Visibilité réduite : +10")

    # Températures extrêmes
    if temperature is not None:
        if temperature <= -5:
            score += 15
            risques.append("Température très basse")
            impacts.append("Risque de verglas, hypothermie ou gêne pour les personnes vulnérables.")
            recommandations.append("Prévoir équipements contre le froid et surveiller les sols glissants.")
            details_score.append("Température très basse : +15")
        elif temperature <= 0:
            score += 8
            risques.append("Température basse")
            impacts.append("Risque local de gel ou verglas.")
            recommandations.append("Vérifier l'état des sols et accès.")
            details_score.append("Température basse : +8")
        elif temperature >= 38:
            score += 15
            risques.append("Température très élevée")
            impacts.append("Risque de malaise, fatigue et déshydratation.")
            recommandations.append("Prévoir hydratation, pauses et protection contre la chaleur.")
            details_score.append("Température très élevée : +15")
        elif temperature >= 32:
            score += 8
            risques.append("Température élevée")
            impacts.append("Risque de fatigue pour les intervenants et personnes fragiles.")
            recommandations.append("Prévoir hydratation et limiter les efforts prolongés.")
            details_score.append("Température élevée : +8")

    # Codes météo dangereux
    if weather_code in [95, 96, 99]:
        score += 25
        risques.append("Risque orageux")
        impacts.append("Risque de foudre, rafales, fortes pluies et perturbations rapides.")
        recommandations.append("Éviter les zones exposées et surveiller l'évolution météo.")
        details_score.append("Orage détecté : +25")
    elif weather_code in [45, 48]:
        score += 10
        risques.append("Brouillard")
        impacts.append("Visibilité potentiellement réduite.")
        recommandations.append("Prévoir une approche prudente et un balisage clair.")
        details_score.append("Brouillard : +10")

    # Couverture nuageuse informative
    if nuages is not None and nuages >= 85:
        impacts.append("Ciel très couvert, conditions lumineuses potentiellement dégradées.")

    # Humidité informative
    if humidite is not None and humidite >= 90:
        impacts.append("Humidité élevée, sensation d'inconfort ou sols possiblement humides.")

    score = min(score, 100)
    niveau = niveau_depuis_score(score)

    if not risques:
        risques.append("Aucun risque météo majeur détecté dans les données disponibles.")

    if not impacts:
        impacts.append("Conditions météo globalement favorables pour une intervention standard.")

    if not recommandations:
        recommandations.append("Maintenir une veille météo simple et confirmer avec les sources officielles.")

    return {
        "score_meteo": score,
        "niveau_meteo": niveau,
        "risques_meteo": risques,
        "impact_intervention": impacts,
        "recommandations": recommandations,
        "details_score": details_score
    }


def geocoder_adresse(adresse: str) -> dict | None:
    url = "https://api-adresse.data.gouv.fr/search/"
    params = {
        "q": adresse,
        "limit": 1
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    if not data.get("features"):
        return None

    feature = data["features"][0]
    props = feature["properties"]
    longitude, latitude = feature["geometry"]["coordinates"]

    return {
        "nom": props.get("label"),
        "pays": "France",
        "latitude": latitude,
        "longitude": longitude,
        "commune": props.get("city"),
        "code_postal": props.get("postcode"),
        "code_commune": props.get("citycode"),
        "source_geocodage": "API Adresse Data Gouv"
    }


def geocoder_ville(ville: str) -> dict | None:
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": ville,
        "count": 1,
        "language": "fr",
        "format": "json"
    }

    response = requests.get(geo_url, params=params, timeout=10)
    response.raise_for_status()
    geo_response = response.json()

    if "results" not in geo_response or not geo_response["results"]:
        return None

    result = geo_response["results"][0]

    return {
        "nom": result["name"],
        "pays": result.get("country", ""),
        "latitude": result["latitude"],
        "longitude": result["longitude"],
        "timezone": result.get("timezone", ""),
        "source_geocodage": "Open-Meteo Geocoding"
    }


def construire_conditions_depuis_current(current: dict) -> dict:
    weather_code = current.get("weather_code")

    return {
        "heure": current.get("time"),
        "temperature_c": current.get("temperature_2m"),
        "temperature_ressentie_c": current.get("apparent_temperature"),
        "humidite_pct": current.get("relative_humidity_2m"),
        "pression_hpa": current.get("pressure_msl"),
        "pression_surface_hpa": current.get("surface_pressure"),
        "vent_km_h": current.get("wind_speed_10m"),
        "rafales_km_h": current.get("wind_gusts_10m"),
        "precipitation_mm": current.get("precipitation"),
        "pluie_mm": current.get("rain"),
        "averses_mm": current.get("showers"),
        "neige_cm": current.get("snowfall"),
        "nuages_pct": current.get("cloud_cover"),
        "visibilite_m": current.get("visibility"),
        "weather_code": weather_code,
        "description": decoder_weather_code(weather_code)
    }


def construire_conditions_depuis_hourly(hourly: dict, index: int) -> dict:
    weather_code = get_hourly_value(hourly, "weather_code", index)

    return {
        "heure": get_hourly_value(hourly, "time", index),
        "temperature_c": get_hourly_value(hourly, "temperature_2m", index),
        "temperature_ressentie_c": get_hourly_value(hourly, "apparent_temperature", index),
        "humidite_pct": get_hourly_value(hourly, "relative_humidity_2m", index),
        "pression_hpa": get_hourly_value(hourly, "pressure_msl", index),
        "vent_km_h": get_hourly_value(hourly, "wind_speed_10m", index),
        "rafales_km_h": get_hourly_value(hourly, "wind_gusts_10m", index),
        "precipitation_mm": get_hourly_value(hourly, "precipitation", index),
        "pluie_mm": get_hourly_value(hourly, "rain", index),
        "averses_mm": get_hourly_value(hourly, "showers", index),
        "neige_cm": get_hourly_value(hourly, "snowfall", index),
        "nuages_pct": get_hourly_value(hourly, "cloud_cover", index),
        "visibilite_m": get_hourly_value(hourly, "visibility", index),
        "weather_code": weather_code,
        "description": decoder_weather_code(weather_code)
    }


def get_hourly_value(hourly: dict, key: str, index: int):
    values = hourly.get(key, [])

    if index < 0 or index >= len(values):
        return None

    return values[index]


def index_plus_proche(hourly_times: list[str], target: datetime) -> int:
    meilleur_index = 0
    meilleur_ecart = None

    for i, time_str in enumerate(hourly_times):
        try:
            dt = datetime.fromisoformat(time_str)
        except ValueError:
            continue

        ecart = abs((dt - target).total_seconds())

        if meilleur_ecart is None or ecart < meilleur_ecart:
            meilleur_ecart = ecart
            meilleur_index = i

    return meilleur_index


def analyser_tendance(analyses: dict) -> dict:
    scores = {
        moment: data.get("analyse", {}).get("score_meteo", 0)
        for moment, data in analyses.items()
    }

    score_actuel = scores.get("actuel", 0)
    score_12h = scores.get("prevision_12h", score_actuel)

    if score_12h > score_actuel + 15:
        tendance = "dégradation prévue"
        commentaire = "Les conditions météo semblent se dégrader dans les prochaines heures."
    elif score_12h < score_actuel - 15:
        tendance = "amélioration prévue"
        commentaire = "Les conditions météo semblent s'améliorer dans les prochaines heures."
    else:
        tendance = "stable"
        commentaire = "Aucune évolution météo majeure n'est détectée sur la période analysée."

    moment_max = max(scores, key=scores.get)

    return {
        "tendance": tendance,
        "commentaire": commentaire,
        "score_max": scores[moment_max],
        "moment_le_plus_defavorable": moment_max
    }


def recuperer_meteo(latitude: float, longitude: float) -> dict:
    weather_url = "https://api.open-meteo.com/v1/forecast"

    variables = [
        "temperature_2m",
        "relative_humidity_2m",
        "apparent_temperature",
        "precipitation",
        "rain",
        "showers",
        "snowfall",
        "cloud_cover",
        "pressure_msl",
        "surface_pressure",
        "wind_speed_10m",
        "wind_gusts_10m",
        "visibility",
        "weather_code"
    ]

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ",".join(variables),
        "hourly": ",".join(variables),
        "forecast_days": 2,
        "timezone": "auto"
    }

    response = requests.get(weather_url, params=params, timeout=15)
    response.raise_for_status()

    return response.json()


def main():
    args = sys.argv[1:]

    if len(args) >= 2 and is_float(args[0]) and is_float(args[1]):
        localisation = {
            "nom": "Coordonnées fournies",
            "pays": "",
            "latitude": float(args[0]),
            "longitude": float(args[1]),
            "timezone": ""
        }
    else:
        requete = " ".join(args) if args else "Paris"

        localisation = geocoder_adresse(requete)

    if localisation is None:
        localisation = geocoder_ville(requete)

    if localisation is None:
        print(json.dumps({
            "error": "Lieu introuvable",
            "requete": requete
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    try:
        weather_response = recuperer_meteo(
            localisation["latitude"],
            localisation["longitude"]
        )
    except requests.RequestException as e:
        print(json.dumps({
            "error": "Erreur lors de l'appel à Open-Meteo",
            "details": str(e)
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    current = weather_response.get("current", {})
    hourly = weather_response.get("hourly", {})
    hourly_times = hourly.get("time", [])

    conditions_actuelles = construire_conditions_depuis_current(current)
    analyse_actuelle = analyser_conditions(conditions_actuelles)

    now_str = current.get("time")

    try:
        now = datetime.fromisoformat(now_str)
    except (TypeError, ValueError):
        now = datetime.now()

    previsions = {}

    for label, heures in [
        ("prevision_3h", 3),
        ("prevision_6h", 6),
        ("prevision_12h", 12),
    ]:
        index = index_plus_proche(hourly_times, now + timedelta(hours=heures))
        conditions = construire_conditions_depuis_hourly(hourly, index)
        analyse = analyser_conditions(conditions)

        previsions[label] = {
            "conditions": conditions,
            "analyse": analyse
        }

    analyses_globales = {
        "actuel": {
            "conditions": conditions_actuelles,
            "analyse": analyse_actuelle
        },
        **previsions
    }

    tendance = analyser_tendance(analyses_globales)

    output = {
        "localisation": localisation,
        "source": "Open-Meteo",
        "conditions_actuelles": conditions_actuelles,
        "analyse_actuelle": analyse_actuelle,
        "previsions": previsions,
        "tendance": tendance,
        "resume_operationnel": {
            "niveau_meteo": analyse_actuelle["niveau_meteo"],
            "score_meteo": analyse_actuelle["score_meteo"],
            "risques_principaux": analyse_actuelle["risques_meteo"],
            "impact_intervention": analyse_actuelle["impact_intervention"],
            "recommandations": analyse_actuelle["recommandations"],
            "evolution_prevue": tendance["tendance"],
            "moment_le_plus_defavorable": tendance["moment_le_plus_defavorable"]
        }
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()