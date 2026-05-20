# Installation du projet

## Présentation

Ce document explique comment installer, configurer et lancer le projet **Emergency Skills Plugin**.

Le projet est développé en Python et utilise plusieurs APIs publiques pour analyser une zone dans un contexte d’urgence.

Il permet notamment de :

- localiser une adresse ;
- récupérer la météo actuelle ;
- rechercher les risques connus d’une commune ;
- identifier des équipements sensibles à proximité ;
- produire une analyse structurée.

## Prérequis

Avant d’installer le projet, il faut disposer de :

- Python 3.10 ou supérieur ;
- pip, le gestionnaire de paquets Python ;
- une connexion Internet ;
- un terminal ou une invite de commandes ;
- Git, optionnel mais recommandé.

Le projet utilise des APIs publiques.  
Dans la version actuelle, aucune clé API n’est obligatoire.

## Récupération du projet

Le projet peut être récupéré de deux manières.

### Méthode 1 : avec Git

Si le projet est disponible sur un dépôt Git, utiliser la commande suivante :

```bash
git clone <url-du-repository>
cd emergency-skills-plugin
```

### Méthode 2 : avec un fichier ZIP

Si le projet est fourni sous forme d’archive ZIP :

1. télécharger le fichier ZIP ;
2. extraire le contenu ;
3. ouvrir un terminal dans le dossier du projet.

Exemple :

```bash
cd emergency-skills-plugin
```

## Structure attendue du projet

Après extraction ou clonage, le projet doit avoir une structure proche de celle-ci :

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
├── agent_urgence.py
├── demo.py
├── requirements.txt
├── .env.example
└── README.md
```

## Création d’un environnement virtuel

Il est recommandé d’utiliser un environnement virtuel Python.

Cela permet d’installer les dépendances du projet sans modifier l’installation globale de Python sur l’ordinateur.

### Sous Windows

Depuis la racine du projet :

```bash
python -m venv .venv
```

Activer ensuite l’environnement virtuel :

```bash
.venv\Scripts\activate
```

Si l’activation fonctionne, le terminal affiche généralement le nom de l’environnement :

```text
(.venv)
```

### Sous Linux ou macOS

Depuis la racine du projet :

```bash
python3 -m venv .venv
```

Activer ensuite l’environnement virtuel :

```bash
source .venv/bin/activate
```

## Installation des dépendances

Une fois l’environnement virtuel activé, installer les dépendances avec :

```bash
pip install -r requirements.txt
```

Les principales dépendances du projet sont :

```text
requests
langchain-core
python-dotenv
```

Si le fichier `requirements.txt` contient beaucoup de dépendances inutiles, il peut être simplifié avec uniquement les bibliothèques réellement utilisées par le projet.

Exemple de `requirements.txt` minimal :

```txt
requests
langchain-core
python-dotenv
```

## Configuration du projet

Le projet contient un fichier :

```text
.env.example
```

Ce fichier sert d’exemple pour les éventuelles variables d’environnement.

Dans la version actuelle du projet, aucune clé API n’est obligatoire, car les APIs utilisées sont publiques.

Il est toutefois possible de créer un fichier `.env` à partir du modèle.

### Sous Windows PowerShell

```powershell
Copy-Item .env.example .env
```

### Sous Linux ou macOS

```bash
cp .env.example .env
```

Exemple de contenu possible pour le fichier `.env` :

```env
APP_ENV=development
DEFAULT_RADIUS=500
```

## Lancement du projet

Pour lancer le projet, se placer à la racine du dossier :

```bash
cd emergency-skills-plugin
```

Puis lancer l’agent principal :

```bash
python agent_urgence.py
```

Le programme peut ensuite recevoir une demande utilisateur.

Exemple :

```text
Analyse la zone 12 rue de la Paix Paris
```

L’agent va alors appeler les skills nécessaires et retourner une analyse structurée de la zone.

## Tester les skills séparément

Chaque skill peut également être lancé indépendamment depuis le terminal.

Cela permet de vérifier que chaque module fonctionne correctement.

## Test du skill `localisation_site`

Ce skill permet de transformer une adresse en coordonnées GPS.

Commande :

```bash
python .claude/skills/localisation_site/main.py "12 rue de la Paix Paris"
```

Résultat attendu :

```json
{
  "requete": "12 rue de la Paix Paris",
  "adresse_trouvee": "12 Rue de la Paix 75002 Paris",
  "commune": "Paris",
  "code_postal": "75002",
  "code_commune": "75102",
  "latitude": 48.869,
  "longitude": 2.331
}
```

## Test du skill `meteo_urgence`

Ce skill permet de récupérer les conditions météo actuelles d’une ville.

Commande :

```bash
python .claude/skills/meteo_urgence/main.py "Paris"
```

Résultat attendu :

```json
{
  "ville": "Paris",
  "pays": "France",
  "latitude": 48.8534,
  "longitude": 2.3488,
  "temperature": 14.3,
  "vent_km_h": 12.5
}
```

## Test du skill `risques_site`

Ce skill permet de rechercher les risques connus d’une commune à partir de son code INSEE.

Commande :

```bash
python .claude/skills/risques_site/main.py 75102
```

Résultat attendu :

```json
{
  "code_insee": "75102",
  "api": "Géorisques",
  "nombre_resultats": 4
}
```

## Test du skill `equipements_sensibles`

Ce skill permet de rechercher les équipements sensibles autour de coordonnées GPS.

Commande :

```bash
python .claude/skills/equipements_sensibles/main.py 48.869 2.331 500
```

Dans cette commande :

- `48.869` correspond à la latitude ;
- `2.331` correspond à la longitude ;
- `500` correspond au rayon de recherche en mètres.

Résultat attendu :

```json
{
  "centre": {
    "latitude": 48.869,
    "longitude": 2.331
  },
  "rayon_m": 500,
  "nombre_equipements": 8,
  "source": "OpenStreetMap / Overpass API"
}
```

## Test du skill `analyse_zone`

Ce skill lance l’analyse complète d’une zone.

Commande :

```bash
python .claude/skills/analyse_zone/main.py "12 rue de la Paix Paris"
```

Résultat attendu :

```json
{
  "requete": "12 rue de la Paix Paris",
  "localisation": {},
  "meteo": {},
  "risques": {},
  "equipements_sensibles": {}
}
```

## Exemple d’utilisation complète

Une fois le projet lancé avec :

```bash
python agent_urgence.py
```

L’utilisateur peut saisir :

```text
Analyse la zone 12 rue de la Paix Paris
```

Le programme exécute alors les étapes suivantes :

1. recherche de l’adresse ;
2. récupération des coordonnées GPS ;
3. identification du code INSEE ;
4. récupération des données météo ;
5. recherche des risques connus ;
6. recherche des équipements sensibles ;
7. affichage d’une réponse structurée.

## Problèmes fréquents

## Python n’est pas reconnu

Si la commande suivante ne fonctionne pas :

```bash
python --version
```

Vérifier que Python est bien installé et ajouté au PATH du système.

Sous Windows, il peut être nécessaire de cocher l’option :

```text
Add Python to PATH
```

lors de l’installation.

## Erreur avec les dépendances

Si une dépendance est manquante, relancer :

```bash
pip install -r requirements.txt
```

Ou installer directement une bibliothèque précise :

```bash
pip install requests
pip install langchain-core
pip install python-dotenv
```

## Erreur avec l’environnement virtuel sous PowerShell

Si PowerShell bloque l’activation de l’environnement virtuel, il peut afficher une erreur liée à la politique d’exécution.

Dans ce cas, lancer PowerShell en tant qu’utilisateur et exécuter :

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Puis réactiver l’environnement :

```powershell
.venv\Scripts\activate
```

## Adresse non trouvée

Si une adresse n’est pas reconnue, essayer avec une adresse plus précise.

Exemple conseillé :

```text
12 rue de la Paix Paris
```

Éviter les adresses trop vagues comme :

```text
Paris
```

pour les tests de géolocalisation précise.

## Erreur API

Le projet dépend de plusieurs APIs externes.

Une erreur peut venir :

- d’une absence de connexion Internet ;
- d’une API temporairement indisponible ;
- d’une limite de requêtes ;
- d’une donnée inexistante pour la zone demandée ;
- d’un format d’entrée incorrect.

Dans ce cas, il faut vérifier :

1. la connexion Internet ;
2. les paramètres fournis au script ;
3. la disponibilité de l’API appelée.

## Bonnes pratiques

Pour garder un projet propre, il est conseillé de ne pas versionner certains fichiers.

Le fichier `.gitignore` peut contenir :

```gitignore
.venv/
__pycache__/
.env
*.pyc
```

Il est aussi conseillé de vérifier que les fichiers suivants sont bien présents avant de rendre le projet :

```text
README.md
requirements.txt
.env.example
docs/architecture.md
docs/installation.md
docs/skills.md
.claude/skills/*/SKILL.md
.claude/skills/*/main.py
```

## Nettoyage avant rendu

Avant de rendre le projet, vérifier que le dossier ne contient pas :

- l’environnement virtuel `.venv/` ;
- les fichiers temporaires Python `__pycache__/` ;
- un fichier `.env` contenant des informations personnelles ;
- des fichiers inutiles générés automatiquement.

La version rendue doit surtout contenir :

- le code source ;
- la documentation ;
- les fichiers de configuration utiles ;
- les fichiers nécessaires à l’installation.

## Conclusion

L’installation du projet **Emergency Skills Plugin** est simple.

Il suffit de :

1. récupérer le projet ;
2. créer un environnement virtuel ;
3. installer les dépendances ;
4. lancer `agent_urgence.py` ;
5. tester l’analyse d’une adresse.

Le projet peut ensuite être enrichi avec de nouveaux skills ou une interface plus complète.