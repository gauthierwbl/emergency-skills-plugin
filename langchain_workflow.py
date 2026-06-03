import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Any

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent

def executer_skill(chemin_relatif: str, arguments: list) -> dict:
    script_path = BASE_DIR / chemin_relatif
    arguments_str = [str(arg) for arg in arguments if arg]
    
    commande = ["python", str(script_path)] + arguments_str
    
    resultat = subprocess.run(
        commande,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    
    if resultat.returncode != 0:
        return {"erreur": f"Échec du skill {chemin_relatif}", "details": resultat.stderr.strip()}
        
    try:
        return json.loads(resultat.stdout)
    except json.JSONDecodeError:
        return {"erreur": "Sortie JSON invalide", "brut": resultat.stdout.strip()}

def collecter_environnement(contexte_geo: dict) -> dict:
    ville = contexte_geo.get("ville", "Paris")
    code_insee = contexte_geo.get("code_insee", "75056")
    
    return {
        "meteo": executer_skill(".claude/skills/meteo_urgence/main.py", [ville]),
        "risques": executer_skill(".claude/skills/risques_site/main.py", [code_insee])
    }

def collecter_sanitaire(contexte_geo: dict) -> dict:
    code_insee = contexte_geo.get("code_insee", "75056")
    return {
        "epidemiologie": executer_skill(".claude/skills/etat_epidemiologique/main.py", ["--code_insee", code_insee])
    }

def collecter_logistique(contexte_geo: dict, destination: str = None) -> dict:
    lat = str(contexte_geo.get("latitude", "48.8566"))
    lon = str(contexte_geo.get("longitude", "2.3522"))
    
    resultats = {
        "equipements": executer_skill(".claude/skills/equipements_sensibles/main.py", [lat, lon, "1000"])
    }
    
    if destination:
        resultats["evacuation"] = executer_skill(
            ".claude/skills/itineraire_evacuation/main.py", 
            ["--lat", lat, "--lon", lon, "--destination", destination]
        )
        
    return resultats

def orchestrer_collecte(etat: Dict[str, Any]) -> Dict[str, Any]:
    analyse = etat.get("analyse_requete", {})
    adresse = analyse.get("adresse")
    domaines = analyse.get("domaines", [])
    
    if not adresse:
        geo = executer_skill(".claude/skills/localisation_utilisateur/main.py", [])
    else:
        geo = executer_skill(".claude/skills/localisation_site/main.py", [adresse])
        
    if "erreur" in geo:
        return {"erreur_critique": "Impossible de localiser la zone.", "details": geo}
    
    donnees = {"localisation": geo}
    
    if "environnement" in domaines:
        donnees["environnement"] = collecter_environnement(geo)
    if "sanitaire" in domaines:
        donnees["sanitaire"] = collecter_sanitaire(geo)
    if "logistique" in domaines:
        donnees["logistique"] = collecter_logistique(geo, analyse.get("destination_evacuation"))
        
    return donnees

def construire_workflow():
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    
    prompt_superviseur = ChatPromptTemplate.from_template(
        "Tu es le Superviseur d'un système d'urgence. Analyse cette demande : '{demande}'.\n"
        "Identifie l'adresse cible. Identifie les domaines d'intervention nécessaires parmi [environnement, sanitaire, logistique]. "
        "Si l'utilisateur demande à fuir vers un endroit, extrais la 'destination_evacuation'.\n"
        "Retourne UNIQUEMENT un JSON structuré avec : 'adresse', 'domaines', et optionnellement 'destination_evacuation'."
    )
    agent_superviseur = prompt_superviseur | llm | JsonOutputParser()

    prompt_evaluateur = ChatPromptTemplate.from_template(
        "Demande initiale : '{demande}'.\n"
        "Données collectées via les scripts : {donnees_brutes}.\n"
        "Vérifie si les données contiennent des erreurs d'exécution (clés 'erreur') ou si elles répondent à la demande. "
        "Retourne UNIQUEMENT un JSON avec 'statut' (complet/erreurs_detectees) et 'remarques' (explication)."
    )
    agent_evaluateur = prompt_evaluateur | llm | JsonOutputParser()

    prompt_redacteur = ChatPromptTemplate.from_template(
        "Tu es l'Agent Rédacteur de crise.\n"
        "Demande de l'utilisateur : {demande}\n"
        "Données factuelles remontées par le terrain : {donnees_brutes}\n"
        "Évaluation du système : {evaluation}\n"
        "Rédige le rapport final d'intervention clair, direct et structuré. Ne mentionne pas le fonctionnement interne du système ou les JSON."
    )
    agent_redacteur = prompt_redacteur | llm | StrOutputParser()

    workflow = (
        RunnablePassthrough.assign(
            analyse_requete=lambda x: agent_superviseur.invoke({"demande": x["demande"]})
        )
        | RunnablePassthrough.assign(
            donnees_brutes=lambda x: orchestrer_collecte(x)
        )
        | RunnablePassthrough.assign(
            evaluation=lambda x: agent_evaluateur.invoke({
                "demande": x["demande"], 
                "donnees_brutes": x["donnees_brutes"]
            })
        )
        | agent_redacteur
    )
    
    return workflow

if __name__ == "__main__":
    print("Emergency Skills Plugin - Agent Gemini Fonctionnel")
    print("==================================================")
    
    requete = input("Situation d'urgence : ").strip()
    if not requete:
        requete = "Je suis au 12 rue de la Paix à Paris, la Seine déborde, je dois évacuer vers Orléans."
        print(f"Test par défaut : {requete}\n")
    
    workflow = construire_workflow()
    print("\n[Traitement en cours... Exécution des sous-agents et des skills Python...]\n")
    
    resultat_final = workflow.invoke({"demande": requete})
    
    print("=== RAPPORT FINAL ===")
    print(resultat_final)