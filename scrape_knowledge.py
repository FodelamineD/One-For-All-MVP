import requests
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

URLS = [
    "https://www.service-public.fr/particuliers/vosdroits/F14202", # PCH
    "https://www.service-public.fr/particuliers/vosdroits/F1654",  # RQTH
    "https://www.service-public.fr/particuliers/vosdroits/F14809"  # AEEH
]

CHROMA_PATH = "./chroma_db"

def scrape_and_index():
    print("[INFO] Demarrage du scraping...")
    documents = []
    
    for url in URLS:
        try:
            print(f"[INFO] Aspiration de {url}...")
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Titre
            h1 = soup.find('h1')
            title = h1.get_text(strip=True) if h1 else "Sans titre"
            
            # Contenu (Targeting precis pour Service-Public)
            content_div = soup.find('div', class_='fiche-item') or soup.find('article') or soup.find('body')
            text = content_div.get_text(separator="\n", strip=True) if content_div else ""
            
            if len(text) < 100:
                print(f"[WARN] Contenu trop court pour {url}")
                continue

            doc = Document(
                page_content=text,
                metadata={"source": url, "title": title}
            )
            documents.append(doc)
            
        except Exception as e:
            print(f"[ERROR] Erreur sur {url}: {e}")

    if documents:
        print(f"[INFO] Sauvegarde de {len(documents)} nouvelles pages dans ChromaDB...")
        db = Chroma.from_documents(
            documents=documents, 
            embedding=OpenAIEmbeddings(),
            persist_directory=CHROMA_PATH
        )
        print("[SUCCESS] Base de connaissances enrichie !")
    else:
        print("[WARN] Aucune donnee recuperee.")

if __name__ == "__main__":
    scrape_and_index()