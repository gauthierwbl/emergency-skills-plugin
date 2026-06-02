# Installation du projet

## Présentation

Ce document explique comment installer, configurer et lancer le projet **Emergency Skills Plugin**.

Le projet utilise :

* Python ;
* plusieurs APIs publiques ;
* Gemini comme agent IA ;
* une architecture modulaire basée sur des skills.

---

# Prérequis

Avant de commencer, vérifier que les éléments suivants sont installés :

* Python 3.10 ou supérieur ;
* pip ;
* Git (recommandé) ;
* connexion Internet ;
* clé API Gemini.

---

# Récupération du projet

## Clonage du dépôt Git

```bash
git clone https://github.com/gauthierwbl/emergency-skills-plugin.git
```

```bash
cd emergency-skills-plugin
```

---

# Structure attendue

```text
emergency-skills-plugin/
│
├── .claude/
│   └── skills/
│
├── docs/
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

# Création d'un environnement virtuel

## Windows

```powershell
python -m venv .venv
```

Activation :

```powershell
.venv\Scripts\activate
```

Le terminal doit afficher :

```text
(.venv)
```

---

## Linux / macOS

```bash
python3 -m venv .venv
```

Activation :

```bash
source .venv/bin/activate
```

---

# Installation des dépendances

Une fois l'environnement activé :

```bash
pip install -r requirements.txt
```

Les principales bibliothèques utilisées sont :

```text
requests
python-dotenv
google-genai
langchain-core
```

---

# Configuration Gemini

Le projet utilise Gemini pour générer les synthèses.

Créer un fichier :

```text
.env
```

à la racine du projet.

Contenu :

```env
GEMINI_API_KEY=votre_cle_api
```

---

# Obtenir une clé Gemini

1. Aller sur :

```text
https://aistudio.google.com/app/apikey
```

2. Se connecter avec un compte Google.

3. Créer une clé API.

4. Copier la clé dans le fichier `.env`.

---

# Vérification de l'installation

Tester un skill simple :

```bash
python .claude/skills/meteo_urgence/main.py Paris
```

Si un résultat JSON apparaît, l'installation fonctionne.

---

# Lancement de l'agent principal

Depuis la racine du projet :

```bash
python agent_gemini.py
```

---

# Exemple d'utilisation

Entrée :

```text
12 rue de la Paix Paris
```

L'agent :

1. localise l'adresse ;
2. récupère la météo ;
3. consulte les risques ;
4. recherche les équipements sensibles ;
5. génère une synthèse Gemini.

---

# Tester les skills individuellement

## Localisation

```bash
python .claude/skills/localisation_site/main.py "12 rue de la Paix Paris"
```

---

## Météo

```bash
python .claude/skills/meteo_urgence/main.py Paris
```

---

## Risques

```bash
python .claude/skills/risques_site/main.py 75102
```

---

## Équipements sensibles

```bash
python .claude/skills/equipements_sensibles/main.py 48.869141 2.331303 500
```

---

## Analyse complète

```bash
python .claude/skills/analyse_zone/main.py "12 rue de la Paix Paris"
```

---

# Problèmes fréquents

## Python non reconnu

Vérifier :

```bash
python --version
```

Si la commande échoue, ajouter Python au PATH.

---

## Environnement virtuel bloqué sous PowerShell

Exécuter :

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Puis réactiver :

```powershell
.venv\Scripts\activate
```

---

## Clé Gemini absente

Erreur typique :

```text
GEMINI_API_KEY manquante
```

Vérifier :

* présence du fichier `.env` ;
* nom exact de la variable ;
* clé correctement copiée.

---

## API indisponible

Certaines APIs publiques peuvent temporairement être indisponibles.

Le projet dépend notamment de :

* Open-Meteo ;
* Géorisques ;
* Overpass API ;
* API Adresse Data Gouv.

---

# Bonnes pratiques Git

Le fichier `.gitignore` doit contenir :

```gitignore
.venv/
__pycache__/
.env
*.pyc
```

Ne jamais envoyer :

* `.env`
* `.venv`
* `__pycache__`

sur GitHub.

---

# Vérifications avant rendu

Les fichiers suivants doivent être présents :

```text
README.md
requirements.txt
.env.example

docs/
├── architecture.md
├── installation.md
└── skills.md

.claude/skills/
```

---

# Conclusion

L'installation du projet nécessite uniquement :

1. Python ;
2. les dépendances du projet ;
3. une clé Gemini ;
4. une connexion Internet.

Une fois installé, l'agent Gemini est capable d'orchestrer plusieurs skills spécialisés afin de produire une analyse complète d'une zone à partir d'une simple adresse.
