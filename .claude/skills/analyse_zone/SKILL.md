---
name: analyse_zone
description: Analyse rapidement une zone ou une adresse en situation d'urgence. Trigger when user asks analyser une zone, analyse d'urgence, situation d'urgence, diagnostic territorial, risques autour d'une adresse, état d'une zone, synthèse opérationnelle.
allowed-tools: Bash(python *)
---

# Skill analyse zone

Ce skill orchestre plusieurs capacités :
- localisation d'une adresse,
- météo actuelle,
- risques connus de la commune.

## Commande

```bash
python ${CLAUDE_SKILL_DIR}/main.py "$ARGUMENTS"