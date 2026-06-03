---
name: etat_epidemiologique
description: Récupère l'état sanitaire et épidémiologique d'une zone. Trigger when user asks "état sanitaire", "épidémie", "maladie", "incidence" ou "virus".
allowed-tools: Bash(python *)
---
# Skill etat_epidemiologique

L'API nécessite un code INSEE de commune. Utilisez d'abord le skill de localisation utilisateur pour obtenir le code INSEE. Le script se chargera de le convertir en région automatiquement.

## Commande

```bash
python ${CLAUDE_SKILL_DIR}/main.py --code_insee "$CODE_INSEE"