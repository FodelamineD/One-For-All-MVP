from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

CHROMA_PATH = "./chroma_db"

def retrieve_context(query: str):
    """Cherche les infos dans la base de données vectorielle."""
    embedding_function = OpenAIEmbeddings()
    # On charge la DB existante
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    
    # Recherche
    results = db.similarity_search(query, k=3)
    
    # On retourne juste le texte brut concaténé
    return "\n\n".join([doc.page_content for doc in results])

def retrieve_context_documents(query: str):
    """Retourne les objets documents bruts (avec métadata) au lieu du texte seul."""
    from langchain_chroma import Chroma
    from langchain_openai import OpenAIEmbeddings
    
    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)
    
    # On récupère les 3 meilleurs docs
    results = db.similarity_search(query, k=3)
    return results