# Emergency Skills Plugin

Projet universitaire visant à créer un système de skills pour assistant IA agentique, capable d’analyser rapidement une zone dans un contexte d’urgence à partir de plusieurs APIs publiques.

## Objectif du projet

Ce projet permet à un assistant IA d’orchestrer plusieurs outils spécialisés afin de produire une première analyse opérationnelle d’une zone.

À partir d’une adresse, le système peut :

- localiser le site ;
- récupérer les conditions météo actuelles ;
- identifier les risques naturels ou technologiques connus ;
- rechercher des équipements sensibles à proximité ;
- générer une synthèse exploitable dans un contexte d’urgence.

L’objectif n’est pas de remplacer les services de secours ou les outils officiels, mais de démontrer comment un assistant IA peut agréger rapidement différentes sources d’information publiques.

## Architecture globale

```text
Utilisateur
   ↓
agent_urgence.py
   ↓
analyse_zone
   ↓
├── localisation_site
├── meteo_urgence
├── risques_site
└── equipements_sensibles
```

## Structure du projet

```text
emergency-skills-plugin/
│
├── .claude/
│   └── skills/
│       ├── analyse_zone/
│       │   ├── main.py
│       │   ├── SKILL.md
│       │   └── references/
│       │
│       ├── equipements_sensibles/
│       │   ├── main.py
│       │   ├── SKILL.md
│       │   └── references/
│       │
│       ├── localisation_site/
│       │   ├── main.py
│       │   ├── SKILL.md
│       │   └── references/
│       │
│       ├── meteo_urgence/
│       │   ├── main.py
│       │   ├── SKILL.md
│       │   └── references/
│       │
│       └── risques_site/
│           ├── main.py
│           ├── SKILL.md
│           └── references/
│
├── docs/
│   ├── architecture.md
│   ├── installation.md
│   └── skills.md
│
├── agent_urgence.py
├── demo.py
├── requirements.txt
├── .env.example
└── README.md
```

## Fonctionnement général

Le projet fonctionne autour d’un agent principal : `agent_urgence.py`.

Cet agent reçoit une demande utilisateur, par exemple une adresse à analyser, puis appelle les différents skills nécessaires.

Le skill principal est `analyse_zone`. Il orchestre les autres skills pour produire une analyse complète :

1. localisation de l’adresse ;
2. récupération des coordonnées GPS ;
3. récupération des données météo ;
4. recherche des risques connus ;
5. recherche des équipements sensibles à proximité ;
6. génération d’un résultat structuré.

## Skills disponibles

| Skill | Rôle |
|---|---|
| `analyse_zone` | Lance l’analyse complète d’une adresse |
| `localisation_site` | Transforme une adresse en coordonnées GPS |
| `meteo_urgence` | Récupère les données météo actuelles |
| `risques_site` | Identifie les risques connus d’une commune |
| `equipements_sensibles` | Recherche les équipements sensibles à proximité |

## APIs utilisées

Le projet s’appuie sur plusieurs APIs publiques.

| API | Utilisation |
|---|---|
| API Adresse data.gouv.fr | Géolocalisation d’une adresse française |
| Open-Meteo | Récupération des données météo actuelles |
| Géorisques | Identification des risques naturels et technologiques |
| OpenStreetMap / Overpass API | Recherche d’équipements sensibles à proximité |

## Installation

### Prérequis

Avant de lancer le projet, il faut disposer de :

- Python 3.10 ou supérieur ;
- pip ;
- une connexion Internet.

### Installation des dépendances

Depuis la racine du projet, exécuter la commande suivante :

```bash
pip install -r requirements.txt
```

## Lancement du projet

Depuis la racine du projet, lancer l’agent principal :

```bash
python agent_urgence.py
```

L’utilisateur peut ensuite saisir une demande comme :

```text
Analyse la zone 12 rue de la Paix Paris
```

Le programme exécute alors les différents skills et retourne une analyse structurée.

## Tester les skills séparément

Chaque skill peut aussi être testé indépendamment.

### Localisation d’une adresse

```bash
python .claude/skills/localisation_site/main.py "12 rue de la Paix Paris"
```

### Analyse météo

```bash
python .claude/skills/meteo_urgence/main.py "Paris"
```

### Recherche des risques

```bash
python .claude/skills/risques_site/main.py 75102
```

### Recherche des équipements sensibles

```bash
python .claude/skills/equipements_sensibles/main.py 48.869 2.331 500
```

### Analyse complète d’une zone

```bash
python .claude/skills/analyse_zone/main.py "12 rue de la Paix Paris"
```

## Exemple de sortie attendue

Le résultat est retourné sous forme de données structurées, généralement au format JSON.

Exemple simplifié :

```json
{
  "requete": "12 rue de la Paix Paris",
  "localisation": {
    "adresse_trouvee": "12 Rue de la Paix 75002 Paris",
    "commune": "Paris",
    "code_postal": "75002",
    "code_commune": "75102",
    "latitude": 48.869,
    "longitude": 2.331
  },
  "meteo": {
    "temperature": 14.3,
    "vent_km_h": 12.5,
    "precipitation_mm": 0
  },
  "risques": {
    "api": "Géorisques",
    "nombre_resultats": 4
  },
  "equipements_sensibles": {
    "nombre_equipements": 8,
    "source": "OpenStreetMap / Overpass API"
  }
}
```

## Documentation

La documentation complète du projet est disponible dans le dossier `docs/`.

| Fichier | Contenu |
|---|---|
| `docs/architecture.md` | Explication de l’architecture du projet |
| `docs/installation.md` | Procédure d’installation et de lancement |
| `docs/skills.md` | Description détaillée des skills |

## Limites du projet

Ce projet est un prototype universitaire.

Il présente plusieurs limites :

- les résultats dépendent de la disponibilité des APIs externes ;
- certaines données peuvent être incomplètes ou non mises à jour ;
- les informations issues d’OpenStreetMap dépendent de données collaboratives ;
- certaines APIs publiques, notamment Overpass API, peuvent parfois répondre lentement ou retourner une erreur temporaire sur des zones très denses comme Paris ;
- le système fonctionne correctement sur d’autres zones, mais cette limite est liée à la disponibilité des services externes ;
- l’analyse produite ne doit pas être utilisée comme seule source dans une vraie situation d’urgence ;
- le système ne remplace pas les autorités, les services de secours ou les outils officiels de gestion de crise.

## Améliorations possibles

Plusieurs évolutions peuvent être envisagées :

- ajouter une interface web ;
- afficher les résultats sur une carte interactive ;
- générer automatiquement un rapport PDF ;
- ajouter un score de criticité ;
- améliorer la gestion des erreurs API ;
- ajouter un système de cache ;
- intégrer les vigilances météo officielles ;
- historiser les analyses effectuées ;
- produire une synthèse plus lisible pour un utilisateur non technique.

## Conclusion

Ce projet montre comment un assistant IA peut utiliser plusieurs skills spécialisés pour analyser rapidement une zone dans un contexte d’urgence.

L’approche modulaire permet de séparer les responsabilités, de faciliter la maintenance et d’ajouter facilement de nouvelles capacités à l’agent.