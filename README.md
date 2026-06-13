# Emergency Skills Plugin

## Présentation

Emergency Skills Plugin est une plateforme expérimentale d'aide à l'analyse de situations d'urgence reposant sur une architecture de skills Claude et un orchestrateur multi‑agents construit avec LangChain.

Le projet agrège automatiquement plusieurs sources de données publiques afin de produire une vue opérationnelle d'une zone géographique : localisation, météo, risques territoriaux, équipements sensibles, cartographie et données sanitaires.

## Fonctionnalités

- Géolocalisation d'adresses et de l'utilisateur
- Analyse météorologique et vigilance
- Analyse des risques naturels et technologiques
- Recherche d'équipements critiques
- Cartographie interactive HTML
- Calcul d'itinéraires d'évacuation
- Analyse épidémiologique territoriale
- Orchestration multi‑agents LangGraph
- Compatibilité Claude et Gemini

## Architecture

Le projet comporte deux couches :

1. **Catalogue de skills** (`.claude/skills/`)
2. **Workflow LangChain** (`langchain.py`)

```text
Utilisateur
    ↓
Agent Géolocalisation
    ↓
Agent Météo
    ↓
Agent Risques
    ↓
Agent Logistique
    ↓
Agent Superviseur
    ↓
Synthèse finale
```

## Skills disponibles

- analyse_zone
- localisation_site
- localisation_utilisateur
- meteo_urgence
- vigilance_meteo
- risques_site
- equipements_sensibles
- cartographie_zone
- itineraire_evacuation
- etat_epidemiologique

## Sources de données

- API Adresse Data Gouv
- Open-Meteo
- Géorisques
- OpenStreetMap / Overpass
- BRouter

## Cas d'usage

- Préparation d'intervention
- Évaluation rapide d'un site
- Gestion de crise
- Formation et démonstration d'architectures agentiques
- Recherche académique sur les systèmes multi‑agents
