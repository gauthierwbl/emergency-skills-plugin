# CLAUDE.md

## Rôle du projet

Ce projet est un prototype universitaire appelé **Emergency Skills Plugin**.

Il vise à démontrer comment un assistant IA agentique peut utiliser plusieurs skills spécialisés pour analyser rapidement une zone dans un contexte d’urgence.

L’assistant doit être capable de :

- comprendre une demande utilisateur en langage naturel ;
- identifier une adresse ou une zone à analyser ;
- appeler les skills adaptés ;
- regrouper les résultats ;
- produire une synthèse claire et structurée.

## Fonctionnement général

Le projet repose sur plusieurs skills présents dans le dossier :

```text
.claude/skills/
```

Chaque skill possède :

- un fichier `main.py` contenant le code Python ;
- un fichier `SKILL.md` décrivant le rôle du skill ;
- un dossier `references/` pour la documentation complémentaire.

## Skills disponibles

| Skill | Rôle |
|---|---|
| `analyse_zone` | Réalise une analyse complète d’une zone |
| `localisation_site` | Localise une adresse et retourne des coordonnées GPS |
| `meteo_urgence` | Récupère les conditions météo actuelles |
| `risques_site` | Recherche les risques connus d’une commune |
| `equipements_sensibles` | Recherche les équipements sensibles à proximité |

## Instruction principale pour l’assistant

Lorsqu’un utilisateur demande d’analyser une zone, l’assistant doit utiliser en priorité le skill :

```text
analyse_zone
```

Ce skill orchestre les autres skills et permet de produire une réponse complète.

## Exemple de demande utilisateur

```text
Analyse la zone 12 rue de la Paix Paris
```

## Comportement attendu

Pour une demande d’analyse de zone, l’assistant doit :

1. identifier l’adresse fournie ;
2. lancer le skill `analyse_zone` ;
3. récupérer les résultats ;
4. présenter une synthèse claire contenant :
   - la localisation ;
   - la météo ;
   - les risques connus ;
   - les équipements sensibles proches.

## Limites

Le projet est un prototype universitaire.

Les résultats dépendent d’APIs publiques externes.  
L’assistant ne doit pas présenter les résultats comme une vérité absolue ou comme une décision officielle.

Le projet ne remplace pas :

- les services de secours ;
- les autorités publiques ;
- les outils professionnels de gestion de crise.