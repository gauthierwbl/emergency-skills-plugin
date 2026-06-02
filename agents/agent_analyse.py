def determiner_niveau_vigilance(donnees: dict) -> str:
    score = 0

    meteo = donnees.get("meteo", {})
    risques = donnees.get("risques", {})
    equipements = donnees.get("equipements_sensibles", {})

    vent = meteo.get("vent_km_h") or 0
    pluie = meteo.get("pluie_mm") or meteo.get("precipitation_mm") or 0

    if vent >= 70:
        score += 30
    elif vent >= 40:
        score += 15

    if pluie >= 20:
        score += 30
    elif pluie >= 5:
        score += 15

    if risques.get("nombre_resultats", 0) > 0:
        score += 25

    if equipements.get("nombre_equipements", 0) >= 10:
        score += 10

    if score >= 60:
        return "élevé"

    if score >= 30:
        return "modéré"

    return "faible"


def analyser_situation(resultat_collecte: dict) -> dict:
    """
    Agent d'analyse.
    Interprète les données collectées et propose une démarche à suivre.
    """

    donnees = resultat_collecte.get("donnees_collectees", {})

    niveau = determiner_niveau_vigilance(donnees)

    facteurs_aggravants = []
    facteurs_rassurants = []

    meteo = donnees.get("meteo", {})
    risques = donnees.get("risques", {})
    equipements = donnees.get("equipements_sensibles", {})

    if meteo.get("vent_km_h", 0) >= 40:
        facteurs_aggravants.append("Vent significatif détecté.")

    if meteo.get("pluie_mm", 0) or meteo.get("precipitation_mm", 0):
        facteurs_aggravants.append("Présence de précipitations.")

    if risques.get("nombre_resultats", 0) > 0:
        facteurs_aggravants.append("Risques territoriaux identifiés.")

    if equipements.get("nombre_equipements", 0) > 0:
        facteurs_rassurants.append("Présence d'équipements sensibles ou utiles à proximité.")

    if not facteurs_aggravants:
        facteurs_rassurants.append("Aucun facteur aggravant majeur détecté dans les données collectées.")

    demarche = [
        "Vérifier les informations auprès des sources officielles.",
        "Identifier les équipements utiles les plus proches.",
        "Évaluer l'accessibilité de la zone.",
        "Surveiller l'évolution météo si la situation est dynamique.",
        "Adapter l'intervention au niveau de vigilance estimé."
    ]

    if niveau == "élevé":
        demarche.insert(0, "Prioriser la sécurisation immédiate de la zone.")
        demarche.insert(1, "Contacter rapidement les services compétents si la situation le justifie.")

    elif niveau == "modéré":
        demarche.insert(0, "Maintenir une surveillance active de la zone.")

    else:
        demarche.insert(0, "Effectuer une vérification simple avant toute décision.")

    return {
        "niveau_vigilance": niveau,
        "facteurs_aggravants": facteurs_aggravants,
        "facteurs_rassurants": facteurs_rassurants,
        "demarche_recommandee": demarche
    }