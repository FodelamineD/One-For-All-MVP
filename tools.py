import os
from dotenv import load_dotenv

# Charge les variables du fichier .env
load_dotenv()

from langchain_core.tools import tool
from rag_tool import retrieve_context
from datetime import datetime, timedelta
from langchain_community.tools.tavily_search import TavilySearchResults

# --- OUTIL 1 : LE RAG ---
@tool
def search_administrative_docs(query: str):
    """Cherche des informations officielles dans les documents PDF."""
    return retrieve_context(query)

# --- OUTIL 2 : CALCULATRICE ---
@tool
def calculate_allowance(montant_base: float, revenus: float):
    """Estime l'allocation."""
    result = montant_base - (revenus * 0.4)
    return max(0, result)

# --- OUTIL 3 : MAÎTRE DU TEMPS ---
@tool
def estimate_processing_time(procedure_type: str):
    """Calcule les délais de réponse."""
    today = datetime.now()
    if "urgence" in procedure_type.lower(): delta = 15
    elif "mdph" in procedure_type.lower(): delta = 120
    else: delta = 60
    estimated = today + timedelta(days=delta)
    return f"Pour une demande {procedure_type} du {today.strftime('%d/%m/%Y')}, réponse vers le {estimated.strftime('%d/%m/%Y')}."

# --- OUTIL 4 : WEB (SÉCURISÉ) ---
# On remet la logique propre : lecture depuis .env
try:
    if os.getenv("TAVILY_API_KEY"):
        # On ne passe PAS la clé en dur ici, LangChain la trouve tout seul dans l'environnement
        web_search_tool = TavilySearchResults(max_results=2)
        ALL_TOOLS = [search_administrative_docs, calculate_allowance, estimate_processing_time, web_search_tool]
    else:
        ALL_TOOLS = [search_administrative_docs, calculate_allowance, estimate_processing_time]
except Exception as e:
    ALL_TOOLS = [search_administrative_docs, calculate_allowance, estimate_processing_time]