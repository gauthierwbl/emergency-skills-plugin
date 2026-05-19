---
name: risques_site
description: Identifie les risques naturels et technologiques d'une commune française à partir d'un code INSEE. Trigger when user asks risques, Géorisques, inondation, séisme, radon, retrait-gonflement argile, mouvement de terrain, cavités, risques industriels, risques commune.
allowed-tools: Bash(python *)
---

# Skill risques site

Utilise l’API Géorisques pour récupérer les risques connus d’une commune française.

## Commande

```bash
python ${CLAUDE_SKILL_DIR}/main.py "$ARGUMENTS"