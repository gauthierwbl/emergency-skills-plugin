# Architecture

## Vision d'ensemble

Le dépôt combine une architecture de skills Claude avec un orchestrateur LangGraph.

### Couche Skills

Chaque compétence métier est encapsulée dans un dossier indépendant :

```text
.claude/skills/<nom_du_skill>/
├── main.py
├── SKILL.md
└── references/
```

### Couche Orchestration

`langchain.py` expose plusieurs outils LangChain puis construit un workflow déterministe.

## Agents

### Agent Géolocalisation
Utilise :
- localisation_site
- localisation_utilisateur

### Agent Météorologie
Utilise :
- meteo_urgence

### Agent Risques
Utilise :
- risques_site

### Agent Logistique
Utilise :
- equipements_sensibles

### Agent Superviseur
Produit la synthèse finale.

## État partagé

EmergencyState contient :

- requete_initiale
- donnees_geographiques
- rapport_meteo
- rapport_risques
- rapport_logistique
- synthese_finale

## Fournisseurs LLM

- Claude 3.5 Sonnet
- Gemini 2.5 Flash

Le fournisseur est sélectionné dynamiquement dans `instantiate_llm()`.
