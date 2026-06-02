---
name: cartographie_zone
description: Génère une carte interactive HTML d'une zone d'intervention avec point central, périmètre et équipements sensibles. Trigger when user asks carte, plan de zone, visualiser une zone, cartographie, vue d'ensemble, plan d'intervention, carte interactive.
allowed-tools: Bash(python *)
---

# Skill cartographie zone

Ce skill génère une carte interactive HTML à partir d'une adresse.

## Commande

```bash
python ${CLAUDE_SKILL_DIR}/main.py "$ARGUMENTS"