from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import os

# Configuration
CHROMA_PATH = "./chroma_db"
# ... et le reste des fonctions

# Configuration
CHROMA_PATH = "./chroma_db"

def retrieve_context(query: str):
    """
    Fonction 1 : Retourne du TEXTE brut (String).
    Utilisée par l'Agent (tools.py) pour lire l'info.
    """
    # Sécurité : On vérifie que la DB existe
    if not os.path.exists(CHROMA_PATH):
        return "Pas de données administratives disponibles (DB manquante)."

    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    
    # Recherche
    results = db.similarity_search(query, k=3)
    
    # Concaténation
    return "\n\n".join([doc.page_content for doc in results])

def retrieve_context_documents(query: str):
    """
    Fonction 2 : Retourne les OBJETS Documents.
    Utilisée par l'Interface (app.py) pour afficher les sources.
    """
    if not os.path.exists(CHROMA_PATH):
        return []

    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    
    results = db.similarity_search(query, k=3)
    return results