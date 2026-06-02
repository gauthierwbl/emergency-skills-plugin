def get_nested(data: dict, *keys, default=None):
    current = data

    for key in keys:
        if not isinstance(current, dict):
            return default

        current = current.get(key)

        if current is None:
            return default

    return current


def calculer_score_vigilance(donnees: dict) -> dict:
    score = 0
    details_score = []

    meteo = donnees.get("meteo", {})
    risques = donnees.get("risques", {})
    equipements = donnees.get("equipements_sensibles", {})

    temperature = meteo.get("temperature")
    vent = meteo.get("vent_km_h") or 0
    pluie = meteo.get("pluie_mm") or meteo.get("precipitation_mm") or 0

    nombre_risques = risques.get("nombre_resultats", 0)
    nombre_equipements = equipements.get("nombre_equipements", 0)

    if vent >= 80:
        score += 30
        details_score.append("Vent très fort détecté : +30")
    elif vent >= 60:
        score += 22
        details_score.append("Vent fort détecté : +22")
    elif vent >= 40:
        score += 12
        details_score.append("Vent significatif détecté : +12")

    if pluie >= 30:
        score += 30
        details_score.append("Précipitations importantes : +30")
    elif pluie >= 10:
        score += 20
        details_score.append("Précipitations modérées : +20")
    elif pluie > 0:
        score += 8
        details_score.append("Présence de précipitations : +8")

    if temperature is not None:
        if temperature <= -5 or temperature >= 38:
            score += 20
            details_score.append("Température extrême : +20")
        elif temperature <= 0 or temperature >= 32:
            score += 10
            details_score.append("Température pouvant aggraver l'intervention : +10")

    if nombre_risques >= 5:
        score += 25
        details_score.append("Plusieurs risques territoriaux identifiés : +25")
    elif nombre_risques > 0:
        score += 15
        details_score.append("Risques territoriaux identifiés : +15")

    if nombre_equipements >= 15:
        score += 10
        details_score.append("Zone dense en équipements sensibles : +10")
    elif nombre_equipements >= 5:
        score += 5
        details_score.append("Présence notable d'équipements sensibles : +5")

    score = min(score, 100)

    if score >= 70:
        niveau = "élevé"
    elif score >= 35:
        niveau = "modéré"
    else:
        niveau = "faible"

    return {
        "score": score,
        "niveau": niveau,
        "details_score": details_score
    }


def analyser_meteo(donnees: dict) -> dict:
    meteo = donnees.get("meteo", {})

    temperature = meteo.get("temperature")
    vent = meteo.get("vent_km_h")
    pluie = meteo.get("pluie_mm") or meteo.get("precipitation_mm")

    constats = []
    vigilance = []

    if temperature is not None:
        constats.append(f"Température actuelle : {temperature} °C.")

        if temperature <= 0:
            vigilance.append("Température basse pouvant compliquer l'intervention.")
        elif temperature >= 32:
            vigilance.append("Température élevée pouvant fatiguer les intervenants ou les personnes vulnérables.")

    if vent is not None:
        constats.append(f"Vent actuel : {vent} km/h.")

        if vent >= 60:
            vigilance.append("Vent fort : prudence avec les objets instables, arbres, échafaudages ou toitures.")
        elif vent >= 40:
            vigilance.append("Vent significatif : surveiller les obstacles et les éléments légers.")

    if pluie is not None:
        constats.append(f"Pluie ou précipitations : {pluie} mm.")

        if pluie >= 10:
            vigilance.append("Précipitations pouvant dégrader l'accessibilité ou augmenter le risque de ruissellement.")
        elif pluie > 0:
            vigilance.append("Présence de pluie : vérifier l'état des accès et sols glissants.")

    if not vigilance:
        vigilance.append("Aucun facteur météo aggravant majeur détecté dans les données disponibles.")

    return {
        "constats": constats,
        "points_vigilance": vigilance
    }


def analyser_risques(donnees: dict) -> dict:
    risques = donnees.get("risques", {})

    nombre = risques.get("nombre_resultats", 0)
    message = risques.get("message")

    constats = []
    vigilance = []

    if message:
        constats.append(message)

    if nombre > 0:
        constats.append(f"{nombre} risque(s) territorial(aux) retourné(s) par l'API.")
        vigilance.append("Consulter les sources officielles pour qualifier précisément les risques.")
    else:
        constats.append("Aucun risque territorial exploitable retourné par l'endpoint utilisé.")
        vigilance.append("Absence de résultat ne signifie pas absence totale de risque.")

    return {
        "constats": constats,
        "points_vigilance": vigilance
    }


def analyser_equipements(donnees: dict) -> dict:
    equipements = donnees.get("equipements_sensibles", {})
    liste = equipements.get("equipements", [])
    nombre = equipements.get("nombre_equipements", 0)

    types = {}
    proches = []

    for equipement in liste:
        type_eq = equipement.get("type", "inconnu")
        types[type_eq] = types.get(type_eq, 0) + 1

        distance = equipement.get("distance_m")

        if distance is not None and distance <= 150:
            proches.append(equipement)

    constats = [
        f"{nombre} équipement(s) sensible(s) ou utile(s) détecté(s) dans le périmètre analysé."
    ]

    if types:
        constats.append(
            "Types détectés : "
            + ", ".join([f"{type_eq} ({nb})" for type_eq, nb in types.items()])
            + "."
        )

    vigilance = []

    if proches:
        vigilance.append("Présence d'équipements très proches de la zone : attention aux personnes vulnérables et à l'accessibilité.")
    elif nombre > 0:
        vigilance.append("Présence d'équipements utiles à proximité, mais pas immédiatement au contact du point central.")
    else:
        vigilance.append("Aucun équipement sensible détecté dans le périmètre : vérifier si le rayon doit être élargi.")

    return {
        "constats": constats,
        "types_detectes": types,
        "equipements_tres_proches": proches[:5],
        "points_vigilance": vigilance
    }


def construire_demarche(niveau: str, analyse_meteo: dict, analyse_risques: dict, analyse_equipements: dict) -> list[str]:
    demarche = []

    if niveau == "élevé":
        demarche.extend([
            "Sécuriser immédiatement la zone et limiter les accès non nécessaires.",
            "Identifier rapidement les personnes vulnérables et les équipements sensibles proches.",
            "Vérifier les risques officiels sur les plateformes institutionnelles.",
            "Contacter ou mobiliser les services compétents si la situation le justifie.",
            "Prévoir une surveillance active de l'évolution météo et de l'accessibilité."
        ])

    elif niveau == "modéré":
        demarche.extend([
            "Effectuer une reconnaissance de la zone avant intervention complète.",
            "Vérifier l'accessibilité des rues et des points d'entrée.",
            "Identifier les équipements sensibles ou utiles dans le périmètre.",
            "Confirmer les informations de risque avec les sources officielles.",
            "Maintenir une surveillance de la météo si la situation peut évoluer."
        ])

    else:
        demarche.extend([
            "Procéder à une vérification simple de la zone.",
            "Confirmer l'adresse et les accès principaux.",
            "Repérer les équipements utiles les plus proches.",
            "Conserver les informations météo et territoriales comme contexte.",
            "Réévaluer la situation si de nouvelles informations apparaissent."
        ])

    points_meteo = " ".join(analyse_meteo.get("points_vigilance", [])).lower()
    points_equipements = " ".join(analyse_equipements.get("points_vigilance", [])).lower()

    if "pluie" in points_meteo or "précipitations" in points_meteo:
        demarche.append("Contrôler l'état des sols, chaussées et accès potentiellement glissants.")

    if "vent" in points_meteo:
        demarche.append("Prendre en compte les objets instables, arbres ou structures exposées au vent.")

    if "personnes vulnérables" in points_equipements:
        demarche.append("Évaluer la présence possible de publics vulnérables autour de la zone.")

    return demarche


def analyser_situation(resultat_collecte: dict) -> dict:
    """
    Agent d'analyse avancé.
    Interprète les données collectées et propose une démarche adaptée.
    """

    donnees = resultat_collecte.get("donnees_collectees", {})

    score_data = calculer_score_vigilance(donnees)
    analyse_meteo = analyser_meteo(donnees)
    analyse_risques = analyser_risques(donnees)
    analyse_equipements = analyser_equipements(donnees)

    facteurs_aggravants = []
    facteurs_rassurants = []

    for point in analyse_meteo.get("points_vigilance", []):
        if "aucun facteur" not in point.lower():
            facteurs_aggravants.append(point)

    for point in analyse_risques.get("points_vigilance", []):
        facteurs_aggravants.append(point)

    equipements = donnees.get("equipements_sensibles", {})

    if equipements.get("nombre_equipements", 0) > 0:
        facteurs_rassurants.append("Des équipements utiles ou sensibles sont identifiés dans le périmètre.")

    if not facteurs_aggravants:
        facteurs_rassurants.append("Aucun facteur aggravant majeur n'a été détecté dans les données disponibles.")

    demarche = construire_demarche(
        score_data["niveau"],
        analyse_meteo,
        analyse_risques,
        analyse_equipements
    )

    lecture_operationnelle = (
        "L'analyse combine les données météo, territoriales et les équipements proches. "
        "Le niveau de vigilance proposé est une aide à la décision et doit être confirmé "
        "avec les sources officielles et l'observation terrain."
    )

    return {
        "score_vigilance": score_data["score"],
        "niveau_vigilance": score_data["niveau"],
        "details_score": score_data["details_score"],
        "analyse_meteo": analyse_meteo,
        "analyse_risques": analyse_risques,
        "analyse_equipements": analyse_equipements,
        "facteurs_aggravants": facteurs_aggravants,
        "facteurs_rassurants": facteurs_rassurants,
        "lecture_operationnelle": lecture_operationnelle,
        "demarche_recommandee": demarche,
        "limites": [
            "Les données proviennent d'APIs publiques et peuvent être incomplètes.",
            "L'absence de résultat ne garantit pas l'absence de danger.",
            "Les informations doivent être confirmées avec les sources officielles et les observations terrain."
        ]
    }