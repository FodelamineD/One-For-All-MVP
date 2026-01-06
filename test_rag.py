import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# 1. SETUP
load_dotenv()
CHROMA_PATH = "./chroma_db"

PROMPT_TEMPLATE = """
Tu es un assistant expert en droits administratifs pour les personnes handicapées.
Réponds à la question en t'basant UNIQUEMENT sur le contexte suivant :

{context}

---
Question : {question}
"""

def query_rag(query_text: str):
    # 2. PRÉPARATION DU LLM & DB
    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # 3. RECHERCHE (RETRIEVAL)
    # On cherche les 3 morceaux (chunks) les plus proches sémantiquement
    print(f"🕵️‍♂️ Recherche dans la base pour : '{query_text}'...")
    results = db.similarity_search(query_text, k=3)

    if len(results) == 0:
        print("❌ Aucune correspondance trouvée.")
        return

    # On colle les morceaux de texte ensemble
    context_text = "\n\n---\n\n".join([doc.page_content for doc in results])
    
    # 4. GÉNÉRATION (GENERATION)
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    print("🤖 Génération de la réponse via GPT-4o...")
    model = ChatOpenAI(model="gpt-4o-mini") # On utilise le mini pour économiser tes sous
    response = model.invoke(prompt)

    # 5. RÉSULTAT
    print("\n" + "="*50)
    print(f"📢 RÉPONSE : \n{response.content}")
    print("="*50)
    
    # Bonus : Afficher les sources pour vérifier qu'il n'invente pas
    print("\n📚 SOURCES UTILISÉES :")
    for doc in results:
        print(f"- {doc.metadata.get('source', 'Inconnu')} (Page {doc.metadata.get('page', '?')})")

if __name__ == "__main__":
    # Change cette question pour tester différents sujets !
    ma_question = "Quelles sont les conditions pour toucher l'AAH ?"
    query_rag(ma_question)