# Documentation des skills

## Présentation générale

Le projet **Emergency Skills Plugin** repose sur un système de skills.

Un skill est un module spécialisé capable de réaliser une tâche précise.  
Dans ce projet, chaque skill permet à l’assistant IA de récupérer ou traiter une information utile dans un contexte d’urgence.

L’objectif est de ne pas avoir un seul gros programme qui fait tout, mais plusieurs modules séparés, chacun avec une responsabilité claire.

## Principe des skills

Chaque skill est placé dans le dossier :

```text
.claude/skills/
```

Chaque sous-dossier correspond à un skill différent.

La structure générale d’un skill est la suivante :

```text
nom_du_skill/
├── main.py
├── SKILL.md
└── references/
```

## Rôle des fichiers d’un skill

### `main.py`

Le fichier `main.py` contient le code Python du skill.

Il permet de :

- récupérer les données d’entrée ;
- appeler une API si nécessaire ;
- traiter les résultats ;
- retourner une réponse structurée.

### `SKILL.md`

Le fichier `SKILL.md` décrit le skill pour l’assistant IA.

Il indique :

- le nom du skill ;
- son objectif ;
- quand l’utiliser ;
- les données attendues ;
- la commande d’exécution ;
- le format de sortie attendu.

### `references/`

Le dossier `references/` peut contenir des documents ou informations complémentaires.

Il peut servir à stocker :

- des exemples ;
- des notes techniques ;
- des références d’API ;
- de la documentation utile au skill.

## Liste des skills du projet

| Skill | Objectif principal |
|---|---|
| `analyse_zone` | Réaliser une analyse complète d’une zone à partir d’une adresse |
| `localisation_site` | Transformer une adresse en coordonnées GPS |
| `meteo_urgence` | Récupérer les conditions météo actuelles |
| `risques_site` | Identifier les risques naturels ou technologiques connus |
| `equipements_sensibles` | Rechercher des équipements sensibles à proximité |

## Vue d’ensemble du fonctionnement

Lorsqu’un utilisateur demande une analyse de zone, le skill principal `analyse_zone` orchestre les autres skills.

```text
analyse_zone
   ↓
localisation_site
   ↓
meteo_urgence
   ↓
risques_site
   ↓
equipements_sensibles
```

Chaque skill renvoie un résultat structuré, généralement au format JSON.

---

# Skill `analyse_zone`

## Objectif

Le skill `analyse_zone` est le skill principal du projet.

Il permet de réaliser une analyse complète d’une zone à partir d’une adresse donnée par l’utilisateur.

Il orchestre plusieurs autres skills afin de produire une réponse globale.

## Rôle dans le projet

Ce skill permet de regrouper plusieurs informations importantes :

- la localisation du site ;
- les coordonnées GPS ;
- les données météo ;
- les risques connus ;
- les équipements sensibles proches.

Il représente donc le cœur du projet.

## Entrée attendue

Le skill attend une adresse sous forme de texte.

Exemple :

```text
12 rue de la Paix Paris
```

## Commande d’exécution

```bash
python .claude/skills/analyse_zone/main.py "12 rue de la Paix Paris"
```

## Étapes réalisées

Le skill effectue généralement les étapes suivantes :

1. réception de l’adresse ;
2. appel du skill `localisation_site` ;
3. récupération du code INSEE, de la latitude et de la longitude ;
4. appel du skill `meteo_urgence` ;
5. appel du skill `risques_site` ;
6. appel du skill `equipements_sensibles` ;
7. regroupement des résultats ;
8. retour d’un résultat structuré.

## Exemple de sortie attendue

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

## Utilité dans un contexte d’urgence

Ce skill permet d’obtenir rapidement une première vision de la situation autour d’une adresse.

Il peut aider à identifier :

- où se situe précisément la zone ;
- les conditions météo qui peuvent aggraver la situation ;
- les risques territoriaux connus ;
- les lieux sensibles ou utiles à proximité.

---

# Skill `localisation_site`

## Objectif

Le skill `localisation_site` permet de transformer une adresse en coordonnées GPS.

Il utilise l’API Adresse officielle de data.gouv.fr.

## Rôle dans le projet

Ce skill est indispensable, car les autres traitements ont besoin de données géographiques.

Il permet notamment de récupérer :

- la latitude ;
- la longitude ;
- la commune ;
- le code postal ;
- le code INSEE.

Le code INSEE est ensuite utilisé pour rechercher les risques connus de la commune.

## Entrée attendue

Le skill attend une adresse sous forme de texte.

Exemple :

```text
12 rue de la Paix Paris
```

## Commande d’exécution

```bash
python .claude/skills/localisation_site/main.py "12 rue de la Paix Paris"
```

## API utilisée

```text
API Adresse data.gouv.fr
```

Cette API permet de rechercher une adresse française et de récupérer ses coordonnées.

## Exemple de sortie attendue

```json
{
  "requete": "12 rue de la Paix Paris",
  "adresse_trouvee": "12 Rue de la Paix 75002 Paris",
  "commune": "Paris",
  "code_postal": "75002",
  "code_commune": "75102",
  "latitude": 48.869,
  "longitude": 2.331,
  "score": 0.95,
  "type": "housenumber"
}
```

## Données importantes retournées

| Donnée | Utilité |
|---|---|
| `adresse_trouvee` | Adresse reconnue par l’API |
| `commune` | Commune associée à l’adresse |
| `code_postal` | Code postal de l’adresse |
| `code_commune` | Code INSEE utilisé pour les risques |
| `latitude` | Coordonnée géographique |
| `longitude` | Coordonnée géographique |
| `score` | Niveau de confiance de la correspondance |

## Utilité dans un contexte d’urgence

La localisation précise est la première étape d’une analyse de zone.

Elle permet de savoir exactement où se situe l’événement ou le site à analyser.

---

# Skill `meteo_urgence`

## Objectif

Le skill `meteo_urgence` permet de récupérer les conditions météo actuelles pour une ville ou une zone donnée.

Il utilise l’API Open-Meteo.

## Rôle dans le projet

La météo peut avoir un impact important dans une situation d’urgence.

Par exemple :

- un vent fort peut aggraver un incendie ;
- de fortes pluies peuvent augmenter un risque d’inondation ;
- une température élevée peut créer un risque sanitaire ;
- une météo défavorable peut compliquer une intervention.

## Entrée attendue

Le skill attend généralement le nom d’une ville.

Exemple :

```text
Paris
```

## Commande d’exécution

```bash
python .claude/skills/meteo_urgence/main.py "Paris"
```

## API utilisée

```text
Open-Meteo
```

Open-Meteo permet d’obtenir des données météorologiques sans clé API obligatoire.

## Exemple de sortie attendue

```json
{
  "ville": "Paris",
  "pays": "France",
  "latitude": 48.8534,
  "longitude": 2.3488,
  "temperature": 14.3,
  "vent_km_h": 12.5,
  "precipitation_mm": 0,
  "pluie_mm": 0
}
```

## Données importantes retournées

| Donnée | Utilité |
|---|---|
| `ville` | Ville analysée |
| `pays` | Pays correspondant |
| `latitude` | Coordonnée GPS |
| `longitude` | Coordonnée GPS |
| `temperature` | Température actuelle |
| `vent_km_h` | Vitesse du vent |
| `precipitation_mm` | Précipitations |
| `pluie_mm` | Quantité de pluie |

## Utilité dans un contexte d’urgence

Les informations météo permettent de mieux comprendre les conditions autour de la zone analysée.

Elles peuvent être utiles pour adapter une réponse ou identifier des facteurs aggravants.

---

# Skill `risques_site`

## Objectif

Le skill `risques_site` permet d’identifier les risques naturels ou technologiques connus pour une commune française.

Il utilise l’API Géorisques.

## Rôle dans le projet

Ce skill permet d’obtenir une première vision des risques présents sur un territoire.

Il peut permettre d’identifier des risques comme :

- les inondations ;
- les mouvements de terrain ;
- les séismes ;
- les risques industriels ;
- les cavités souterraines ;
- le retrait-gonflement des argiles.

## Entrée attendue

Le skill attend un code INSEE de commune.

Exemple :

```text
75102
```

## Commande d’exécution

```bash
python .claude/skills/risques_site/main.py 75102
```

## API utilisée

```text
Géorisques
```

Géorisques est une plateforme officielle française permettant d’obtenir des informations sur les risques naturels et technologiques.

## Exemple de sortie attendue

```json
{
  "code_insee": "75102",
  "api": "Géorisques",
  "endpoint": "gaspar/risques",
  "nombre_resultats": 4,
  "donnees": []
}
```

## Données importantes retournées

| Donnée | Utilité |
|---|---|
| `code_insee` | Identifie la commune |
| `api` | Source des données |
| `endpoint` | Point d’accès utilisé |
| `nombre_resultats` | Nombre de risques trouvés |
| `donnees` | Liste des informations retournées |

## Utilité dans un contexte d’urgence

La connaissance des risques territoriaux permet d’adapter l’analyse d’une zone.

Par exemple, une adresse située dans une commune exposée aux inondations ne sera pas analysée de la même manière qu’une adresse située dans une zone à risque industriel.

---

# Skill `equipements_sensibles`

## Objectif

Le skill `equipements_sensibles` permet de rechercher des équipements sensibles autour d’une position GPS.

Il utilise les données OpenStreetMap via Overpass API.

## Rôle dans le projet

Ce skill permet d’identifier rapidement les lieux sensibles ou utiles autour d’une zone.

Il peut rechercher notamment :

- des hôpitaux ;
- des pharmacies ;
- des écoles ;
- des cliniques ;
- des casernes de pompiers ;
- des postes de police.

## Entrée attendue

Le skill attend trois informations :

```text
latitude longitude rayon
```

Exemple :

```text
48.869 2.331 500
```

Dans cet exemple :

- `48.869` correspond à la latitude ;
- `2.331` correspond à la longitude ;
- `500` correspond au rayon de recherche en mètres.

## Commande d’exécution

```bash
python .claude/skills/equipements_sensibles/main.py 48.869 2.331 500
```

## API utilisée

```text
OpenStreetMap / Overpass API
```

Overpass API permet d’interroger les données OpenStreetMap autour d’une position géographique.

## Exemple de sortie attendue

```json
{
  "centre": {
    "latitude": 48.869,
    "longitude": 2.331
  },
  "rayon_m": 500,
  "nombre_equipements": 3,
  "equipements": [
    {
      "nom": "Pharmacie Centrale",
      "type": "pharmacy",
      "latitude": 48.868,
      "longitude": 2.330,
      "distance_m": 120
    }
  ],
  "source": "OpenStreetMap / Overpass API"
}
```

## Données importantes retournées

| Donnée | Utilité |
|---|---|
| `centre` | Point GPS de référence |
| `rayon_m` | Rayon de recherche |
| `nombre_equipements` | Nombre d’équipements trouvés |
| `equipements` | Liste des lieux identifiés |
| `source` | Source des données |

## Utilité dans un contexte d’urgence

Ce skill peut être utile pour identifier :

- des lieux vulnérables ;
- des services de secours ;
- des établissements recevant du public ;
- des points d’appui possibles ;
- des zones nécessitant une attention particulière.

---

# Résumé des entrées et sorties

| Skill | Entrée | Sortie principale |
|---|---|---|
| `analyse_zone` | Adresse | Analyse complète |
| `localisation_site` | Adresse | Coordonnées GPS + code INSEE |
| `meteo_urgence` | Ville | Données météo |
| `risques_site` | Code INSEE | Risques connus |
| `equipements_sensibles` | Latitude, longitude, rayon | Équipements proches |

---

# Exemple de scénario complet

## Demande utilisateur

```text
Analyse la zone 12 rue de la Paix Paris
```

## Déroulement interne

```text
1. L’utilisateur fournit une adresse.
2. Le skill analyse_zone reçoit la demande.
3. Le skill localisation_site récupère les coordonnées GPS.
4. Le skill meteo_urgence récupère les données météo.
5. Le skill risques_site recherche les risques connus.
6. Le skill equipements_sensibles recherche les équipements proches.
7. Les résultats sont regroupés.
8. Une synthèse structurée est retournée.
```

## Résultat attendu

```json
{
  "requete": "12 rue de la Paix Paris",
  "localisation": {
    "commune": "Paris",
    "latitude": 48.869,
    "longitude": 2.331
  },
  "meteo": {
    "temperature": 14.3,
    "vent_km_h": 12.5
  },
  "risques": {
    "nombre_resultats": 4
  },
  "equipements_sensibles": {
    "nombre_equipements": 8
  }
}
```

---

# Format des réponses

Les skills retournent principalement des données au format JSON.

Ce format a plusieurs avantages :

- il est facile à lire par un programme ;
- il est compatible avec une future interface web ;
- il permet de structurer clairement les résultats ;
- il facilite l’exploitation par un assistant IA ;
- il peut être utilisé pour générer un rapport.

---

# Gestion des erreurs

Dans la version actuelle, la gestion des erreurs reste simple.

Les erreurs possibles sont par exemple :

- adresse introuvable ;
- ville inconnue ;
- code INSEE incorrect ;
- API temporairement indisponible ;
- absence de connexion Internet ;
- format d’entrée incorrect.

Une amélioration possible serait de standardiser toutes les erreurs avec un format commun.

Exemple :

```json
{
  "erreur": true,
  "message": "Adresse introuvable",
  "source": "localisation_site"
}
```

---

# Limites des skills

Les skills dépendent fortement des APIs externes.

Les résultats peuvent donc être incomplets ou indisponibles si :

- une API ne répond pas ;
- les données ne sont pas disponibles pour la zone demandée ;
- les informations OpenStreetMap sont incomplètes ;
- l’adresse fournie est trop vague ;
- le code INSEE est incorrect.

Le projet reste un prototype universitaire et ne doit pas être utilisé comme seul outil dans une situation réelle d’urgence.

---

# Améliorations possibles

Plusieurs améliorations pourraient être apportées aux skills :

- améliorer la gestion des erreurs ;
- ajouter un format de réponse commun à tous les skills ;
- ajouter un score de criticité ;
- ajouter un skill de vigilance météo officielle ;
- ajouter un skill de génération de rapport PDF ;
- ajouter un skill de cartographie ;
- permettre l’analyse de plusieurs adresses ;
- ajouter un système de cache ;
- historiser les analyses ;
- enrichir la recherche d’équipements sensibles.

---

# Conclusion

Les skills du projet **Emergency Skills Plugin** permettent de découper l’analyse d’une zone en plusieurs modules spécialisés.

Cette organisation rend le projet plus clair, plus maintenable et plus évolutif.

Le skill `analyse_zone` joue le rôle d’orchestrateur principal, tandis que les autres skills fournissent chacun une information précise nécessaire à l’analyse globale.