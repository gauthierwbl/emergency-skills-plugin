# Emergency Skills Plugin

Projet universitaire visant à créer un système de skills pour assistant IA agentique, capable d'analyser rapidement une zone dans un contexte d'urgence grâce à plusieurs APIs publiques.

---

# Objectif du projet

Ce projet a pour objectif de démontrer comment un assistant IA peut orchestrer plusieurs outils spécialisés afin de produire une analyse rapide et contextualisée d'une zone géographique.

À partir d'une adresse, le système est capable de :

* localiser précisément le site ;
* récupérer les conditions météorologiques actuelles ;
* identifier les risques territoriaux connus ;
* rechercher les équipements sensibles à proximité ;
* produire une synthèse rédigée par une intelligence artificielle.

L'objectif n'est pas de remplacer les services de secours ou les plateformes officielles, mais de montrer comment une architecture agentique peut agréger efficacement différentes sources d'information publiques.

---

# Architecture globale

```text
Utilisateur
      ↓
agent_gemini.py
      ↓
analyse_zone
      ↓
├── localisation_site
├── meteo_urgence
├── risques_site
└── equipements_sensibles
```

---

# Architecture du projet

```text
emergency-skills-plugin/
│
├── .claude/
│   └── skills/
│       ├── analyse_zone/
│       ├── equipements_sensibles/
│       ├── localisation_site/
│       ├── meteo_urgence/
│       └── risques_site/
│
├── docs/
│   ├── architecture.md
│   ├── installation.md
│   └── skills.md
│
├── tests/
│
├── .env.example
├── .gitignore
├── agent_gemini.py
├── requirements.txt
└── README.md
```

---

# Fonctionnement général

Le projet repose sur un agent principal : `agent_gemini.py`.

Cet agent reçoit une demande utilisateur, exécute le skill principal `analyse_zone`, récupère les informations provenant de plusieurs APIs puis utilise Gemini pour produire une synthèse rédigée et contextualisée.

Workflow :

1. saisie d'une adresse ;
2. géolocalisation ;
3. récupération des coordonnées GPS ;
4. récupération des données météo ;
5. récupération des risques territoriaux ;
6. recherche des équipements sensibles ;
7. génération d'une synthèse par Gemini.

---

# Agent IA Gemini

Le projet utilise Gemini comme agent décisionnel.

L'agent :

* interprète la demande utilisateur ;
* exécute les skills nécessaires ;
* agrège les données retournées ;
* produit une synthèse en langage naturel ;
* estime un niveau de vigilance ;
* formule des recommandations.

Cette approche permet de combiner des données structurées avec les capacités de synthèse d'un modèle de langage.

---

# Skills disponibles

| Skill                 | Description                                     |
| --------------------- | ----------------------------------------------- |
| analyse_zone          | Lance une analyse complète d'une adresse        |
| localisation_site     | Transforme une adresse en coordonnées GPS       |
| meteo_urgence         | Récupère les conditions météo actuelles         |
| risques_site          | Recherche les risques connus d'une commune      |
| equipements_sensibles | Recherche les équipements sensibles à proximité |

---

# APIs utilisées

## API Adresse Data Gouv

Utilisée pour :

* géocoder une adresse ;
* récupérer les coordonnées GPS ;
* récupérer les informations administratives.

Documentation :

https://adresse.data.gouv.fr/

---

## Open-Meteo

Utilisée pour :

* température ;
* vitesse du vent ;
* pluie ;
* précipitations.

Documentation :

https://open-meteo.com/

---

## Géorisques

Utilisée pour :

* risques naturels ;
* risques technologiques ;
* informations territoriales.

Documentation :

https://www.georisques.gouv.fr/

---

## OpenStreetMap / Overpass API

Utilisée pour :

* hôpitaux ;
* pharmacies ;
* écoles ;
* services de police ;
* casernes de pompiers ;
* équipements sensibles.

Documentation :

https://overpass-api.de/

---

# Installation

## Prérequis

* Python 3.10 ou supérieur
* Connexion Internet
* Clé API Gemini

---

## Cloner le dépôt

```bash
git clone https://github.com/gauthierwbl/emergency-skills-plugin.git
```

```bash
cd emergency-skills-plugin
```

---

## Créer un environnement virtuel

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

---

## Installer les dépendances

```bash
pip install -r requirements.txt
```

---

## Configuration Gemini

Créer un fichier `.env` à la racine du projet :

```env
GEMINI_API_KEY=votre_cle_api
```

Le fichier `.env` ne doit jamais être envoyé sur GitHub.

Le fichier `.env.example` sert de modèle.

---

# Lancement du projet

Depuis la racine du projet :

```bash
python agent_gemini.py
```

Exemple :

```text
12 rue de la Paix Paris
```

L'agent :

* collecte les données ;
* exécute les skills ;
* génère une synthèse opérationnelle.

---

# Tester les skills individuellement

## Localisation

```bash
python .claude/skills/localisation_site/main.py "12 rue de la Paix Paris"
```

## Météo

```bash
python .claude/skills/meteo_urgence/main.py Paris
```

## Risques

```bash
python .claude/skills/risques_site/main.py 75102
```

## Équipements sensibles

```bash
python .claude/skills/equipements_sensibles/main.py 48.869141 2.331303 500
```

## Analyse complète

```bash
python .claude/skills/analyse_zone/main.py "12 rue de la Paix Paris"
```

---

# Exemple de workflow

```text
Demande utilisateur
        ↓
Analyse d'une adresse
        ↓
Localisation
        ↓
Météo
        ↓
Risques
        ↓
Équipements sensibles
        ↓
Synthèse Gemini
```

---

# Documentation

Une documentation détaillée est disponible dans le dossier `docs`.

| Fichier              | Description                     |
| -------------------- | ------------------------------- |
| docs/architecture.md | Architecture générale du projet |
| docs/installation.md | Guide d'installation            |
| docs/skills.md       | Documentation des skills        |

---

# Limites du projet

Ce projet est un prototype universitaire.

Les résultats dépendent :

* de la disponibilité des APIs publiques ;
* de la qualité des données OpenStreetMap ;
* de la disponibilité des services Géorisques ;
* des limitations de quota des APIs utilisées.

Certaines APIs, notamment Overpass API, peuvent occasionnellement répondre lentement ou retourner une erreur temporaire sur des zones très denses.

Les résultats fournis ne doivent pas être utilisés comme unique source d'information dans une situation d'urgence réelle.

---

# Perspectives d'amélioration

Les évolutions suivantes sont envisagées :

* génération automatique de rapports PDF ;
* calcul d'un score de criticité ;
* visualisation cartographique ;
* interface web ;
* historisation des analyses ;
* ajout de nouvelles sources de données ;
* architecture multi-agents ;
* génération de recommandations avancées.

---

# Conclusion

Ce projet met en œuvre une architecture agentique moderne combinant :

* un agent IA (Gemini) ;
* des skills spécialisés ;
* plusieurs APIs publiques ;
* une logique d'orchestration.

L'approche modulaire facilite la maintenance, la réutilisation des composants et l'ajout de nouvelles fonctionnalités.

Le projet illustre concrètement les concepts de skills, d'agents, de workflows et d'orchestration d'outils dans un contexte d'analyse territoriale et d'aide à la décision.
