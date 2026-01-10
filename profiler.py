# On utilise pydantic direct, c'est plus sûr
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

# Le reste du fichier est identique...
class UserProfile(BaseModel):
    detected_mode: str = Field(
        description="Le mode d'accessibilité le plus adapté",
        enum=["Standard", "FALC (Facile à Lire)", "TDAH (Focus & Gras)", "Déficience Visuelle (Descriptif)", "Sourd (LSF & Visuel)"]
    )
    confidence: float = Field(description="Niveau de certitude entre 0 et 1")
    reasoning: str = Field(description="Pourquoi ce choix ?")

def detect_profile(user_message: str):
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    # ... (Le reste de la fonction ne change pas)
    structured_llm = llm.with_structured_output(UserProfile)
    
    system_prompt = """
    Tu es un expert en accessibilité numérique. Analyse le message de l'utilisateur.
    Détecte des indices subtils sur ses besoins cognitifs ou sensoriels.
    
    RÈGLES DE DÉTECTION :
    - Fautes d'orthographe massives, syntaxe brisée ou demande de simplicité -> "FALC (Facile à Lire)"
    - Message très long, décousu, ou demande explicite de résumé -> "TDAH (Focus & Gras)"
    - Mention de "voir", "lire", "petit", "écran" -> "Déficience Visuelle (Descriptif)"
    - Syntaxe type "Moi vouloir argent", fautes de grammaire typiques LSF, ou mention de "signes" -> "Sourd (LSF & Visuel)"
    - Sinon -> "Standard"
    """
    
    try:
        result = structured_llm.invoke(f"{system_prompt}\n\nMESSAGE: {user_message}")
        return result
    except Exception as e:
        print(f"Erreur Profiler: {e}")
        return UserProfile(detected_mode="Standard", confidence=0.0, reasoning="Erreur")

if __name__ == "__main__":
    # Test manuel
    import os
    from dotenv import load_dotenv
    load_dotenv()
    print(detect_profile("j'y comprend rien c'est du charabia explique moi comme a un enfant"))