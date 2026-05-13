---
name: meteo_urgence
description: Donne les conditions météo et prévisions d'urgence pour une ville ou des coordonnées GPS. Trigger when user asks météo, température, pluie, vent, vigilance, prévisions météo, conditions météo dangereuses, intempéries, weather forecast.
allowed-tools: Bash(python *)
---

# Skill météo urgence

Utilise le script Python du skill pour récupérer les données météo depuis OpenMeteo.

## Commande

```bash
python ${CLAUDE_SKILL_DIR}/main.py "$ARGUMENTS"