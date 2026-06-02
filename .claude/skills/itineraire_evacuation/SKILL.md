---
name: itineraire_evacuation
description: Calcule un itinéraire d'évacuation en contournant spécifiquement une zone de danger, puis ouvre une carte interactive. Trigger when user asks "évacuer", "itinéraire de secours", "fuir la zone", "trajet d'évacuation".
allowed-tools: Bash(python *)
---
# Skill itineraire_evacuation

Ce skill utilise BRouter pour calculer un trajet qui évite physiquement un périmètre de danger (nogos).

L'agent doit déterminer la destination de repli de manière logique avant d'appeler ce skill.

## Commande

```bash
python ${CLAUDE_SKILL_DIR}/main.py --lat "$USER_LAT" --lon "$USER_LON" --destination "$DESTINATION" --danger_lat "$DANGER_LAT" --danger_lon "$DANGER_LON" --danger_rayon "$RAYON_EN_METRES"