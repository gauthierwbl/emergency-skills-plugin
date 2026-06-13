# Installation

## Prérequis

- Python 3.10+
- Accès Internet
- Clé API Anthropic ou Gemini

## Installation

```bash
git clone <repository>
cd emergency-skills-plugin
pip install -r requirements.txt
```

## Variables d'environnement

```env
ANTHROPIC_API_KEY=...
GEMINI_API_KEY=...
```

## Exécution

```bash
python langchain.py
```

## Structure recommandée

```text
.claude/
docs/
outputs/
langchain.py
requirements.txt
README.md
```
