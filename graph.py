import os
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# Import de ton outil RAG
from rag_tool import retrieve_context

load_dotenv()

# 1. DÉFINITION DE LA MÉMOIRE (STATE)
# C'est ici qu'on stocke toute la conversation
class State(TypedDict):
    # "add_messages" permet d'ajouter les nouveaux messages à la liste existante (append)
    messages: Annotated[list, add_messages]

# ... (Tes imports restent pareils)

def chatbot_node(state: State):
    llm = ChatOpenAI(model="gpt-4o-mini")
    
    # On récupère le dernier message
    last_message = state["messages"][-1].content
    
    # On récupère le profil utilisateur s'il existe (sinon défaut)
    # LangGraph stocke tout dans le state, on va tricher un peu pour le MVP
    # et l'injecter via le SystemPrompt direct.
    
    context = retrieve_context(last_message)
    
    # 🚨 LA NOUVEAUTÉ EST ICI : LE PROMPT DYNAMIQUE
    # On définit comment l'IA doit parler selon le profil choisi dans l'UI
    # (Note: Dans une version V2, ce serait passé proprement dans le state)
    user_profile = "Standard" 
    # Petite astuce : on va choper le profil depuis le dernier message humain 
    # s'il contient une méta-data (hack MVP) ou on le laisse générique.
    # Pour l'instant, on va gérer ça dans le Prompt Template directement.

    prompt = f"""
    Tu es l'assistant One For All.
    
    CONTEXTE DOCUMENTAIRE :
    {context}
    
    CONSIGNES D'ADAPTATION :
    - Si l'utilisateur demande du FALC (Facile à Lire), fais des phrases courtes, mots simples, listes à puces.
    - Si l'utilisateur a un TDAH, mets en GRAS les mots clés importants et sois ultra-concis.
    - Sinon, réponds normalement mais poliment.
    
    Réponds à la question en utilisant le contexte. Si tu ne sais pas, dis-le.
    """
    
    messages = [SystemMessage(content=prompt)] + state["messages"]
    response = llm.invoke(messages)
    
    return {"messages": [response]}

# 3. CONSTRUCTION DU GRAPHE
workflow = StateGraph(State)

# On ajoute notre noeud unique
workflow.add_node("chatbot", chatbot_node)

# On définit le flux : Début -> Chatbot -> Fin
workflow.add_edge(START, "chatbot")
workflow.add_edge("chatbot", END)

# On compile le cerveau
app = workflow.compile()

# ==========================================
# TEST RAPIDE (Simulation de conversation)
# ==========================================
if __name__ == "__main__":
    print("🧠 Démarrage du Cerveau LangGraph...")
    
    # Simulation d'un utilisateur qui pose 2 questions à la suite
    inputs = {"messages": [HumanMessage(content="Quelles sont les conditions de l'AAH ?")]}
    
    # 1ère réponse
    print("\n--- Tour 1 ---")
    for event in app.stream(inputs):
        for value in event.values():
            print("🤖 Agent:", value["messages"][-1].content)
            
    # On simule la mémoire en gardant l'état (dans la vraie vie, l'interface gérera ça)
    # Pour ce test simple, on lance juste une 2ème question indépendante pour vérifier que ça ne plante pas
    print("\n--- Tour 2 ---")
    inputs2 = {"messages": [HumanMessage(content="Et pour la MDPH, je fais comment ?")]}
    for event in app.stream(inputs2):
        for value in event.values():
            print("🤖 Agent:", value["messages"][-1].content)