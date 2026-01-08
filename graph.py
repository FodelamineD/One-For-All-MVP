import os
from dotenv import load_dotenv
from typing import Annotated, Literal
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition # La magie est ici

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from tools import ALL_TOOLS # On importe ta boîte à outils

load_dotenv()

# 1. DÉFINITION DE L'ÉTAT (STATE)
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 2. INITIALISATION DU MODÈLE AVEC OUTILS
# On dit au LLM : "Voici tes outils, utilise-les si besoin."
llm = ChatOpenAI(model="gpt-4o") # On prend le gros modèle pour qu'il soit malin
llm_with_tools = llm.bind_tools(ALL_TOOLS)

# 3. LE NOEUD "AGENT" (Le Décideur)
def agent_node(state: State):
    # L'agent reçoit l'historique et décide quoi faire (Parler ou Appeler un outil)
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# 4. CONSTRUCTION DU GRAPHE
workflow = StateGraph(State)

# Node 1 : L'Agent (Cerveau)
workflow.add_node("agent", agent_node)
# Node 2 : L'Exécuteur d'Outils (C'est LangGraph qui gère l'exécution technique)
workflow.add_node("tools", ToolNode(ALL_TOOLS))

# LE ROUTING INTELLIGENT
workflow.add_edge(START, "agent")

# Conditionnelle :
# Si l'agent a décidé d'appeler un outil -> On va vers "tools"
# Si l'agent a juste répondu (texte) -> On va vers END
workflow.add_conditional_edges(
    "agent",
    tools_condition,
)

# Après avoir exécuté un outil, on revient TOUJOURS à l'agent pour qu'il analyse le résultat
workflow.add_edge("tools", "agent")

# Compile
app = workflow.compile()