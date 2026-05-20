import requests
import sys
import json


def calculer_vigilance(temperature, vent, precipitation, pluie):
    """
    Calcule un niveau de vigilance météo simple à partir de seuils internes.
    Ce score n'est pas une vigilance officielle Météo-France.
    """

    score = 0
    facteurs = []

    if vent is not None:
        if vent >= 80:
            score += 3
            facteurs.append("Vent très fort")
        elif vent >= 60:
            score += 2
            facteurs.append("Vent fort")
        elif vent >= 40:
            score += 1
            facteurs.append("Vent modéré à fort")

    if precipitation is not None:
        if precipitation >= 30:
            score += 3
            facteurs.append("Précipitations très importantes")
        elif precipitation >= 15:
            score += 2
            facteurs.append("Précipitations importantes")
        elif precipitation >= 5:
            score += 1
            facteurs.append("Précipitations modérées")

    if pluie is not None:
        if pluie >= 20:
            score += 2
            facteurs.append("Pluie importante")
        elif pluie >= 5:
            score += 1
            facteurs.append("Pluie modérée")

    if temperature is not None:
        if temperature >= 35:
            score += 3
            facteurs.append("Température très élevée")
        elif temperature >= 30:
            score += 2
            facteurs.append("Forte chaleur")
        elif temperature <= -5:
            score += 2
            facteurs.append("Température très basse")
        elif temperature <= 0:
            score += 1
            facteurs.append("Risque de gel")

    if score == 0:
        niveau = "faible"
        couleur = "vert"
    elif score <= 2:
        niveau = "modéré"
        couleur = "jaune"
    elif score <= 4:
        niveau = "élevé"
        couleur = "orange"
    else:
        niveau = "critique"
        couleur = "rouge"

    return {
        "score": score,
        "niveau": niveau,
        "couleur": couleur,
        "facteurs": facteurs
    }


def vigilance_meteo(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,wind_speed_10m,precipitation,rain"
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()
    current = data.get("current", {})

    temperature = current.get("temperature_2m")
    vent = current.get("wind_speed_10m")
    precipitation = current.get("precipitation")
    pluie = current.get("rain")

    vigilance = calculer_vigilance(
        temperature,
        vent,
        precipitation,
        pluie
    )

    return {
        "latitude": latitude,
        "longitude": longitude,
        "meteo_actuelle": {
            "temperature": temperature,
            "vent_km_h": vent,
            "precipitation_mm": precipitation,
            "pluie_mm": pluie
        },
        "vigilance_estimee": vigilance,
        "source": "Open-Meteo",
        "avertissement": "Cette vigilance est une estimation interne au prototype et ne remplace pas les vigilances officielles."
    }


def main():
    if len(sys.argv) < 3:
        print(json.dumps({
            "error": "Latitude et longitude requises",
            "exemple": "python main.py 47.63796 6.86289"
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    try:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])

        resultat = vigilance_meteo(latitude, longitude)

        print(json.dumps(resultat, ensure_ascii=False, indent=2))

    except ValueError:
        print(json.dumps({
            "error": "Latitude ou longitude invalide"
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    except requests.RequestException as e:
        print(json.dumps({
            "error": "Erreur lors de l'appel à l'API météo",
            "details": str(e),
            "source": "Open-Meteo"
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    except Exception as e:
        print(json.dumps({
            "error": "Erreur inattendue",
            "details": str(e)
        }, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()