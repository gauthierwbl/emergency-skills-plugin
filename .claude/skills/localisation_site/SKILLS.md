---
name: localisation_site
description: Localise une adresse, un lieu ou un site en France. Trigger when user asks coordonnées GPS, localiser une adresse, géocoder, commune, code postal, latitude, longitude, adresse, site d'urgence, où se trouve.
allowed-tools: Bash(python *)
---

# Skill localisation site

Utilise l’API Adresse du gouvernement français pour convertir une adresse ou un lieu en coordonnées GPS.

## Commande

```bash
python ${CLAUDE_SKILL_DIR}/main.py "$ARGUMENTS"