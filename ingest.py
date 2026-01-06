import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# Charge la clé depuis le .env
load_dotenv()

DATA_PATH = "./data"
CHROMA_PATH = "./chroma_db"

def ingest_documents():
    # 1. Check API Key
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("ERREUR : Pas de clé API trouvée. Vérifie ton fichier .env !")

    # 2. SCAN
    print(f"📂 Scanning {DATA_PATH}...")
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Le dossier {DATA_PATH} n'existe pas.")
    
    loader = PyPDFDirectoryLoader(DATA_PATH)
    raw_documents = loader.load()
    print(f"📄 {len(raw_documents)} pages chargées.")

    # 3. SPLIT
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(raw_documents)
    print(f"🧩 {len(chunks)} fragments générés.")

    # 4. STORE (C'est là que ça utilise tes crédits)
    print("💾 Génération des embeddings via OpenAI...")
    db = Chroma.from_documents(
        documents=chunks, 
        embedding=OpenAIEmbeddings(),
        persist_directory=CHROMA_PATH
    )
    print(f"✅ SUCCÈS : Base de données créée dans {CHROMA_PATH}.")

if __name__ == "__main__":
    ingest_documents()