---
name: equipements_sensibles
description: Recherche les équipements sensibles autour de coordonnées GPS ou d'une adresse. Trigger when user asks hôpitaux, écoles, pharmacies, casernes, équipements sensibles, établissements à proximité, secours, lieux vulnérables, autour d'une zone.
allowed-tools: Bash(python *)
---

# Skill équipements sensibles

Utilise OpenStreetMap via Overpass API pour identifier des équipements sensibles autour d’une zone.

## Commande

```bash
python ${CLAUDE_SKILL_DIR}/main.py "$ARGUMENTS"