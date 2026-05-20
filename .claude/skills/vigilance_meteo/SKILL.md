---
name: vigilance_meteo
description: Trigger when user asks for weather alert, vigilance météo, weather risk, dangerous weather conditions, wind risk, rain risk, heat risk, cold risk, or emergency weather assessment for GPS coordinates.
allowed-tools: Bash(python *)
---

# Skill `vigilance_meteo`

## Objectif

Ce skill estime un niveau de vigilance météo à partir de coordonnées GPS.

Il utilise les données météo actuelles fournies par Open-Meteo, puis applique des seuils simples pour produire une vigilance estimée.

## Quand utiliser ce skill

Utiliser ce skill lorsque l'utilisateur demande :

- une vigilance météo ;
- un risque météo ;
- une évaluation des conditions météo dangereuses ;
- une analyse du vent, de la pluie, de la chaleur ou du froid ;
- une aide à la décision météo dans un contexte d'urgence.

## Entrée attendue

Le skill attend deux arguments :

```text
latitude longitude
```

Exemple :

```bash
python ${CLAUDE_SKILL_DIR}/main.py 47.63796 6.86289
```

## Sortie

La sortie est au format JSON.

Elle contient :

- les coordonnées GPS ;
- les données météo actuelles ;
- un score de vigilance ;
- un niveau estimé ;
- une couleur associée ;
- les facteurs aggravants détectés.

## Niveaux possibles

| Score | Niveau | Couleur |
|---|---|---|
| 0 | faible | vert |
| 1 à 2 | modéré | jaune |
| 3 à 4 | élevé | orange |
| 5 ou plus | critique | rouge |

## Important

Cette vigilance est une estimation interne au prototype.

Elle ne remplace pas les vigilances officielles, les autorités publiques, les services de secours ou les outils professionnels de gestion de crise.