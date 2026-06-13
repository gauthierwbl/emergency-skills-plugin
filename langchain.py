import subprocess
import sys
import warnings
from pathlib import Path
from typing import TypedDict
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent

# Masquer l'avertissement de dépréciation de LangGraph V1.0 pour un affichage propre
warnings.filterwarnings("ignore", category=DeprecationWarning)

PROJECT_ROOT = Path(__file__).resolve().parent

def execute_python_script(relative_path: str, arguments: list[str]) -> str:
    script_path = str(PROJECT_ROOT / relative_path)
    result = subprocess.run(
        ["python", script_path] + arguments,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    if result.returncode != 0:
        print(f"\n[ERREUR D'EXÉCUTION] {script_path}\n{result.stderr}", file=sys.stderr)
        return result.stderr
    return result.stdout

@tool
def outil_localiser_site(adresse: str) -> str:
    """Localise une adresse et renvoie les coordonnées GPS et le code INSEE."""
    return execute_python_script(".claude/skills/localisation_site/main.py", [adresse])

@tool
def outil_localiser_utilisateur() -> str:
    """Récupère la position actuelle de l'utilisateur (GPS, ville, code INSEE)."""
    return execute_python_script(".claude/skills/localisation_utilisateur/main.py", [])

@tool
def outil_meteo_urgence(ville: str) -> str:
    """Renvoie la météo d'urgence pour une ville ou des coordonnées."""
    return execute_python_script(".claude/skills/meteo_urgence/main.py", [ville])

@tool
def outil_risques_site(code_insee: str) -> str:
    """Analyse les risques naturels et technologiques via le code INSEE."""
    return execute_python_script(".claude/skills/risques_site/main.py", [code_insee])

@tool
def outil_equipements_sensibles(latitude: str, longitude: str) -> str:
    """Recherche les équipements sensibles autour des coordonnées GPS."""
    return execute_python_script(".claude/skills/equipements_sensibles/main.py", [latitude, longitude, "1000"])

class EmergencyState(TypedDict):
    requete_initiale: str
    donnees_geographiques: str
    rapport_meteo: str
    rapport_risques: str
    rapport_logistique: str
    synthese_finale: str

def instantiate_llm(provider: str):
    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model="claude-3-5-sonnet-latest", temperature=0)
    
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

def build_deterministic_workflow(llm_provider: str):
    llm = instantiate_llm(llm_provider)

    agent_geolocalisation = create_react_agent(
        llm,
        tools=[outil_localiser_site, outil_localiser_utilisateur],
        prompt="Tu es l'Agent Géolocalisation. Si une adresse est demandée, utilise outil_localiser_site. Si la position actuelle est demandée, utilise outil_localiser_utilisateur. Renvoie uniquement les données GPS et INSEE factuelles."
    )

    agent_meteo = create_react_agent(
        llm,
        tools=[outil_meteo_urgence],
        prompt="Tu es l'Agent Météorologie. Utilise le contexte géographique fourni pour récupérer la météo via ton outil. Rédige un rapport factuel."
    )

    agent_risques = create_react_agent(
        llm,
        tools=[outil_risques_site],
        prompt="Tu es l'Agent Risques. Utilise le code INSEE fourni pour récupérer les risques via ton outil. Rédige un rapport factuel."
    )

    agent_logistique = create_react_agent(
        llm,
        tools=[outil_equipements_sensibles],
        prompt="Tu es l'Agent Logistique. Utilise la latitude et longitude fournies pour lister les équipements sensibles via ton outil. Rédige un rapport factuel."
    )

    def node_geolocalisation(state: EmergencyState) -> EmergencyState:
        response = agent_geolocalisation.invoke({"messages": [HumanMessage(content=state["requete_initiale"])]})
        return {"donnees_geographiques": response["messages"][-1].content}

    def node_meteo(state: EmergencyState) -> EmergencyState:
        context = f"Contexte géographique : {state['donnees_geographiques']}"
        response = agent_meteo.invoke({"messages": [HumanMessage(content=context)]})
        return {"rapport_meteo": response["messages"][-1].content}

    def node_risques(state: EmergencyState) -> EmergencyState:
        context = f"Contexte géographique : {state['donnees_geographiques']}"
        response = agent_risques.invoke({"messages": [HumanMessage(content=context)]})
        return {"rapport_risques": response["messages"][-1].content}

    def node_logistique(state: EmergencyState) -> EmergencyState:
        context = f"Contexte géographique : {state['donnees_geographiques']}"
        response = agent_logistique.invoke({"messages": [HumanMessage(content=context)]})
        return {"rapport_logistique": response["messages"][-1].content}

    def node_superviseur(state: EmergencyState) -> EmergencyState:
        synthesis_prompt = (
            f"Requête initiale : {state['requete_initiale']}\n\n"
            f"--- Géographie ---\n{state.get('donnees_geographiques', '')}\n\n"
            f"--- Météorologie ---\n{state.get('rapport_meteo', '')}\n\n"
            f"--- Risques ---\n{state.get('rapport_risques', '')}\n\n"
            f"--- Logistique ---\n{state.get('rapport_logistique', '')}\n\n"
            "Rédige la synthèse opérationnelle finale structurée à partir de ces rapports."
        )
        response = llm.invoke([
            SystemMessage(content="Tu es l'Agent Superviseur. Tu consolides les rapports terrain en une synthèse claire."),
            HumanMessage(content=synthesis_prompt)
        ])
        return {"synthese_finale": response.content}

    workflow_graph = StateGraph(EmergencyState)
    
    workflow_graph.add_node("agent_geolocalisation", node_geolocalisation)
    workflow_graph.add_node("agent_meteo", node_meteo)
    workflow_graph.add_node("agent_risques", node_risques)
    workflow_graph.add_node("agent_logistique", node_logistique)
    workflow_graph.add_node("agent_superviseur", node_superviseur)

    workflow_graph.add_edge(START, "agent_geolocalisation")
    workflow_graph.add_edge("agent_geolocalisation", "agent_meteo")
    workflow_graph.add_edge("agent_meteo", "agent_risques")
    workflow_graph.add_edge("agent_risques", "agent_logistique")
    workflow_graph.add_edge("agent_logistique", "agent_superviseur")
    workflow_graph.add_edge("agent_superviseur", END)

    return workflow_graph.compile()

if __name__ == "__main__":
    load_dotenv()
    
    SELECTED_PROVIDER = "google" 
    emergency_workflow = build_deterministic_workflow(SELECTED_PROVIDER)
    
    adresse_saisie = input("Entrez l'adresse (laissez vide pour utiliser votre position IP) : ").strip()
    
    if adresse_saisie:
        requete_formatee = f"Localise cette adresse : {adresse_saisie}"
    else:
        requete_formatee = "Récupère ma position actuelle."
        
    initial_state = {"requete_initiale": requete_formatee}
    final_output = emergency_workflow.invoke(initial_state)
    
    print("\n=== RAPPORT FINAL INTER-AGENTS ===")
    print(final_output["synthese_finale"])