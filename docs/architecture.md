# Architecture du projet

## Présentation générale

Le projet **Emergency Skills Plugin** repose sur une architecture agentique modulaire.

L'objectif est de permettre à une intelligence artificielle de coordonner plusieurs outils spécialisés afin d'analyser rapidement une zone géographique dans un contexte d'urgence.

Chaque fonctionnalité métier est encapsulée dans un skill indépendant, ce qui facilite la maintenance, les tests et les évolutions futures.

---

# Architecture générale

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

# Rôle des composants

## Agent Gemini

L'agent principal du projet est :

```text
agent_gemini.py
```

Il joue le rôle d'orchestrateur.

Ses responsabilités sont :

* recevoir la demande utilisateur ;
* lancer les analyses nécessaires ;
* récupérer les résultats retournés par les skills ;
* transmettre les données à Gemini ;
* générer une synthèse compréhensible pour un utilisateur.

L'agent constitue le point d'entrée principal du projet.

---

## Skill analyse_zone

Le skill :

```text
analyse_zone
```

est le skill central.

Il coordonne plusieurs traitements :

1. géolocalisation ;
2. récupération météo ;
3. analyse des risques ;
4. recherche des équipements sensibles.

Il regroupe ensuite les résultats dans une structure JSON unique.

---

## Skill localisation_site

Responsable de :

* convertir une adresse en coordonnées GPS ;
* récupérer :

  * latitude ;
  * longitude ;
  * commune ;
  * code postal ;
  * code INSEE.

API utilisée :

```text
API Adresse Data Gouv
```

---

## Skill meteo_urgence

Responsable de :

* récupérer la température ;
* récupérer la vitesse du vent ;
* récupérer les précipitations ;
* récupérer les informations météo utiles à l'analyse.

API utilisée :

```text
Open-Meteo
```

---

## Skill risques_site

Responsable de :

* rechercher les risques territoriaux connus ;
* récupérer les informations Géorisques ;
* analyser une commune à partir de son code INSEE.

API utilisée :

```text
Géorisques
```

---

## Skill equipements_sensibles

Responsable de :

* rechercher les équipements proches ;
* identifier :

  * hôpitaux ;
  * pharmacies ;
  * écoles ;
  * services de police ;
  * casernes de pompiers ;
  * cliniques.

API utilisée :

```text
OpenStreetMap / Overpass API
```

---

# Workflow complet

Lorsqu'un utilisateur saisit :

```text
12 rue de la Paix Paris
```

le système exécute les étapes suivantes :

```text
Adresse utilisateur
        ↓
analyse_zone
        ↓
localisation_site
        ↓
Coordonnées GPS
        ↓
meteo_urgence
        ↓
risques_site
        ↓
equipements_sensibles
        ↓
Résultat JSON
        ↓
Gemini
        ↓
Synthèse finale
```

---

# Structure du projet

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
├── .env
├── .env.example
├── .gitignore
├── agent_gemini.py
├── requirements.txt
└── README.md
```

---

# Communication entre les composants

Le projet repose sur une communication simple entre les différents modules.

Principe :

```text
agent_gemini.py
        ↓
appel du skill
        ↓
main.py
        ↓
API externe
        ↓
JSON
        ↓
agent_gemini.py
        ↓
Gemini
        ↓
Synthèse
```

Chaque skill reste indépendant et peut être exécuté seul.

---

# APIs utilisées

## API Adresse Data Gouv

Utilisée pour :

* géocoder une adresse ;
* récupérer les coordonnées GPS ;
* récupérer les informations administratives.

---

## Open-Meteo

Utilisée pour :

* température ;
* vent ;
* pluie ;
* précipitations.

---

## Géorisques

Utilisée pour :

* risques naturels ;
* risques technologiques ;
* informations territoriales.

---

## OpenStreetMap / Overpass API

Utilisée pour :

* hôpitaux ;
* pharmacies ;
* écoles ;
* police ;
* pompiers ;
* équipements sensibles.

---

# Avantages de cette architecture

## Modularité

Chaque skill est indépendant.

## Réutilisabilité

Les skills peuvent être utilisés seuls ou combinés.

## Maintenabilité

Chaque fonctionnalité est isolée.

## Évolutivité

De nouveaux skills peuvent être ajoutés facilement.

## Approche agentique

L'agent utilise plusieurs outils spécialisés pour répondre à une demande complexe.

---

# Limites actuelles

Le projet reste un prototype universitaire.

Certaines limites existent :

* dépendance aux APIs publiques ;
* absence de cache ;
* absence de base de données ;
* absence d'interface graphique ;
* appels synchrones ;
* dépendance à une connexion Internet.

---

# Perspectives d'évolution

Plusieurs améliorations sont envisageables :

* génération automatique de rapports PDF ;
* calcul d'un score de criticité ;
* visualisation cartographique ;
* interface web ;
* historisation des analyses ;
* architecture multi-agents ;
* intégration de nouvelles sources de données ;
* analyse de plusieurs zones simultanément.

---

# Conclusion

L'architecture du projet repose sur une séparation claire entre l'agent, les skills et les sources de données.

Cette organisation permet de construire un système flexible, évolutif et facilement maintenable, tout en illustrant les principes modernes des architectures agentiques basées sur des outils spécialisés.
