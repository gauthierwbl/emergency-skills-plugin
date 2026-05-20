# Architecture du projet

## Présentation générale

Le projet **Emergency Skills Plugin** repose sur une architecture modulaire basée sur des skills.

Chaque skill correspond à une capacité précise de l’assistant IA.  
L’objectif est de permettre à l’agent de ne pas tout faire directement dans un seul fichier, mais d’appeler plusieurs modules spécialisés selon la demande utilisateur.

Cette architecture permet de rendre le projet :

- plus lisible ;
- plus facile à maintenir ;
- plus simple à faire évoluer ;
- plus proche du fonctionnement d’un assistant IA agentique.

## Objectif de l’architecture

L’architecture du projet a été pensée pour permettre à un assistant IA d’analyser rapidement une zone géographique dans un contexte d’urgence.

À partir d’une simple adresse, l’agent peut :

1. localiser le site ;
2. récupérer les coordonnées GPS ;
3. identifier la commune et son code INSEE ;
4. récupérer les conditions météo actuelles ;
5. consulter les risques connus sur la commune ;
6. rechercher les équipements sensibles à proximité ;
7. regrouper les résultats dans une synthèse exploitable.

## Schéma global

```text
Utilisateur
   │
   │ Demande en langage naturel
   ↓
agent_urgence.py
   │
   │ Appel du skill principal
   ↓
analyse_zone
   │
   ├── localisation_site
   │       └── API Adresse data.gouv.fr
   │
   ├── meteo_urgence
   │       └── Open-Meteo
   │
   ├── risques_site
   │       └── API Géorisques
   │
   └── equipements_sensibles
           └── OpenStreetMap / Overpass API
```

## Structure des dossiers

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

## Rôle des principaux fichiers

### `agent_urgence.py`

Le fichier `agent_urgence.py` est le point d’entrée principal du projet.

Il sert à faire le lien entre la demande utilisateur et les skills disponibles.  
Il reçoit une demande en langage naturel, puis déclenche les traitements adaptés.

Son rôle est de :

- recevoir une demande utilisateur ;
- appeler le bon skill ;
- récupérer les résultats ;
- afficher une réponse structurée.

Dans le projet, il permet notamment d’appeler l’analyse complète d’une zone à partir d’une adresse.

### `demo.py`

Le fichier `demo.py` peut servir à montrer rapidement le fonctionnement du projet.

Il peut être utilisé pour tester un scénario simple sans passer par une utilisation complète de l’agent.

### `.claude/skills/`

Le dossier `.claude/skills/` contient l’ensemble des skills du projet.

Chaque sous-dossier correspond à un skill indépendant.

Exemple :

```text
.claude/skills/localisation_site/
```

Chaque skill possède généralement :

```text
main.py
SKILL.md
references/
```

### `main.py`

Le fichier `main.py` contient le code Python du skill.

Il est responsable de :

- récupérer les paramètres d’entrée ;
- appeler une API si nécessaire ;
- traiter les données reçues ;
- retourner un résultat structuré, souvent au format JSON.

### `SKILL.md`

Le fichier `SKILL.md` décrit le fonctionnement du skill pour l’assistant IA.

Il précise généralement :

- le nom du skill ;
- son objectif ;
- les cas où il doit être utilisé ;
- la manière de l’exécuter ;
- les données attendues en entrée ;
- les données retournées en sortie.

### `references/`

Le dossier `references/` peut contenir des informations complémentaires utiles au skill.

Il peut servir à stocker :

- de la documentation ;
- des exemples ;
- des notes techniques ;
- des références d’API ;
- des fichiers utiles au fonctionnement ou à la compréhension du skill.

### `docs/`

Le dossier `docs/` contient la documentation générale du projet.

Il est composé de plusieurs fichiers :

| Fichier | Rôle |
|---|---|
| `architecture.md` | Explique l’organisation technique du projet |
| `installation.md` | Explique comment installer et lancer le projet |
| `skills.md` | Présente les skills disponibles et leur fonctionnement |

## Principe de fonctionnement

Le projet fonctionne en plusieurs étapes.

Lorsqu’un utilisateur demande une analyse de zone, par exemple :

```text
Analyse la zone 12 rue de la Paix Paris
```

L’agent va lancer une chaîne de traitements.

## Étape 1 : réception de la demande

L’utilisateur saisit une adresse ou une demande en langage naturel.

Exemple :

```text
Analyse la zone 12 rue de la Paix Paris
```

Cette demande est reçue par `agent_urgence.py`.

## Étape 2 : appel du skill principal

L’agent appelle le skill principal `analyse_zone`.

Ce skill est responsable de coordonner les autres skills du projet.

Il ne se limite pas à une seule API : il regroupe plusieurs sources d’information pour produire une analyse complète.

## Étape 3 : localisation du site

Le skill `analyse_zone` commence par appeler le skill `localisation_site`.

Ce skill transforme l’adresse en informations géographiques.

Il récupère notamment :

- l’adresse trouvée ;
- la commune ;
- le code postal ;
- le code INSEE ;
- la latitude ;
- la longitude.

Ces informations sont indispensables pour les autres traitements.

## Étape 4 : récupération de la météo

Une fois la localisation obtenue, le projet peut récupérer les conditions météorologiques actuelles.

Le skill `meteo_urgence` permet d’obtenir des données comme :

- la température ;
- la vitesse du vent ;
- les précipitations ;
- la pluie éventuelle.

Ces informations peuvent être importantes dans un contexte d’urgence, car la météo peut aggraver certaines situations.

## Étape 5 : recherche des risques connus

Le skill `risques_site` utilise le code INSEE de la commune pour rechercher les risques connus.

Il peut permettre d’identifier des risques comme :

- les inondations ;
- les mouvements de terrain ;
- les risques sismiques ;
- les risques industriels ;
- le retrait-gonflement des argiles ;
- les cavités souterraines.

Ces informations permettent d’avoir une première vision du contexte territorial.

## Étape 6 : recherche des équipements sensibles

Le skill `equipements_sensibles` utilise les coordonnées GPS du site pour rechercher les équipements sensibles situés à proximité.

Il peut rechercher des lieux comme :

- les hôpitaux ;
- les pharmacies ;
- les écoles ;
- les casernes de pompiers ;
- les postes de police ;
- les cliniques.

Ces informations peuvent aider à identifier les lieux vulnérables ou utiles autour de la zone analysée.

## Étape 7 : regroupement des résultats

Une fois les différents skills exécutés, le projet regroupe les résultats dans une réponse structurée.

Le résultat final peut contenir :

```json
{
  "requete": "12 rue de la Paix Paris",
  "localisation": {},
  "meteo": {},
  "risques": {},
  "equipements_sensibles": {}
}
```

Cette structure rend les résultats facilement exploitables par :

- un assistant IA ;
- une interface web ;
- un script ;
- un futur système de génération de rapport.

## Communication entre les composants

Les différents composants communiquent principalement à travers des appels de scripts Python.

Le principe général est le suivant :

```text
agent_urgence.py
   ↓
appel d’un script Python
   ↓
main.py du skill concerné
   ↓
appel éventuel à une API externe
   ↓
résultat JSON
   ↓
retour à l’agent
```

Cette approche permet à chaque skill de rester indépendant.

## APIs externes utilisées

### API Adresse data.gouv.fr

Cette API permet de convertir une adresse française en coordonnées GPS.

Elle est utilisée par le skill :

```text
localisation_site
```

Elle permet de récupérer :

- une adresse normalisée ;
- une commune ;
- un code postal ;
- un code INSEE ;
- une latitude ;
- une longitude.

### Open-Meteo

Open-Meteo permet de récupérer des données météorologiques actuelles.

Elle est utilisée par le skill :

```text
meteo_urgence
```

Elle permet de récupérer :

- la température ;
- le vent ;
- les précipitations ;
- certaines informations météo utiles à l’analyse.

### Géorisques

Géorisques permet d’obtenir des informations sur les risques naturels et technologiques connus.

Elle est utilisée par le skill :

```text
risques_site
```

Elle permet de récupérer des informations liées à une commune française à partir de son code INSEE.

### OpenStreetMap / Overpass API

Overpass API permet d’interroger les données OpenStreetMap.

Elle est utilisée par le skill :

```text
equipements_sensibles
```

Elle permet de rechercher des équipements autour d’une position GPS.

## Avantages de cette architecture

Cette architecture présente plusieurs avantages.

### Modularité

Chaque skill est séparé dans son propre dossier.

Cela permet de modifier un skill sans impacter directement les autres.

### Lisibilité

Le projet est plus facile à comprendre, car chaque partie a un rôle précis.

Par exemple :

- un skill pour la localisation ;
- un skill pour la météo ;
- un skill pour les risques ;
- un skill pour les équipements sensibles.

### Évolutivité

Il est possible d’ajouter de nouveaux skills sans réécrire toute l’application.

Par exemple, on pourrait ajouter :

- un skill de vigilance météo ;
- un skill de génération de rapport PDF ;
- un skill de cartographie ;
- un skill d’analyse de criticité.

### Réutilisabilité

Un skill peut être utilisé seul ou dans une analyse complète.

Par exemple, `localisation_site` peut être utilisé indépendamment de `analyse_zone`.

### Maintenance facilitée

En cas d’erreur sur une API ou sur un traitement, il est plus simple d’identifier le skill concerné.

## Limites de l’architecture actuelle

L’architecture actuelle reste celle d’un prototype universitaire.

Elle présente donc certaines limites :

- les appels API sont dépendants d’une connexion Internet ;
- il n’y a pas encore de cache local ;
- il n’y a pas de base de données ;
- la gestion des erreurs reste simple ;
- les résultats ne sont pas affichés sur une carte ;
- l’interface utilisateur est limitée ;
- les appels sont principalement synchrones.

## Améliorations possibles

Plusieurs améliorations pourraient être apportées :

- ajouter une interface web ;
- afficher les résultats sur une carte interactive ;
- ajouter un système de cache pour éviter les appels API répétés ;
- améliorer la gestion des erreurs ;
- ajouter une base de données pour historiser les analyses ;
- créer une génération automatique de rapports PDF ;
- intégrer les vigilances météo officielles ;
- ajouter un score de criticité de la zone ;
- enrichir les équipements sensibles recherchés ;
- permettre l’analyse de plusieurs adresses en une seule fois.

## Conclusion

L’architecture du projet **Emergency Skills Plugin** repose sur une séparation claire des responsabilités.

Chaque skill possède une mission précise, ce qui rend le projet plus propre, plus maintenable et plus facilement extensible.

Cette organisation illustre le fonctionnement d’un assistant IA agentique capable d’orchestrer plusieurs outils spécialisés pour produire une analyse rapide et structurée d’une zone dans un contexte d’urgence.