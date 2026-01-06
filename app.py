import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from graph import app as brain
from openai import OpenAI # On a besoin du client direct pour l'audio
from rag_tool import retrieve_context_documents
import streamlit as st
import os
# ... tes autres imports ...

# 👇 AJOUTE CE BLOC ICI 👇
# BOOTLOADER : Vérification de la base de données au démarrage
CHROMA_PATH = "./chroma_db"

if not os.path.exists(CHROMA_PATH):
    # Si le dossier n'existe pas, on lance l'ingestion automatiquement
    with st.spinner("🧠 Initialisation de la mémoire (Première exécution)..."):
        # On importe ton script d'ingestion comme un module
        import ingest
        # On force la création de la DB
        try:
            ingest.ingest_documents()
            st.success("✅ Mémoire construite avec succès !")
        except Exception as e:
            st.error(f"Erreur critique lors de l'ingestion : {e}")
            st.stop()
# 👆 FIN DU BLOC 👆

# ... La suite de ton code (st.set_page_config, etc.) ...
st.set_page_config(page_title="One For All", page_icon="♾️", layout="wide")

# --- SIDEBAR : CONFIGURATION UTILISATEUR ---
# --- SIDEBAR : CONFIGURATION & OUTILS ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/accessibility2.png", width=80)
    st.header("🎛️ Configuration")
    
    # 1. Choix du Handicap
    handicap_mode = st.radio(
        "Mode d'adaptation :",
        ["Standard", "FALC (Facile à Lire)", "TDAH (Focus & Gras)", "Déficience Visuelle (Descriptif)"]
    )
    st.info(f"Mode activé : **{handicap_mode}**")
    
    st.markdown("---")
    
    # 2. LE MICRO (DÉPLACÉ ICI) 🎙️
    st.header("🗣️ Mode Vocal")
    audio_value = st.audio_input("Cliquez pour enregistrer")
    if audio_value:
        st.caption("✅ Audio capturé. Traitement en cours...")

    st.markdown("---")
    st.caption("One For All - MVP v1.2")

# --- MEMOIRE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage historique
for message in st.session_state.messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(message.content)

# --- SAISIE ---
# --- SAISIE (MULTIMODAL : TEXTE + VOCAL) ---
# --- SAISIE PRINCIPALE ---
# Le micro est géré dans la sidebar, ici on gère juste le texte
text_input = st.chat_input("Écrivez votre question ici...")

# LOGIQUE DE PRIORITÉ : AUDIO > TEXTE
final_user_input = None

if audio_value:
    # Si on a parlé dans la sidebar, on traite l'audio
    # Pas besoin de spinner ici, Streamlit gère le reload
    try:
        client = OpenAI()
        transcription = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_value
        )
        final_user_input = transcription.text
    except Exception as e:
        st.sidebar.error(f"Erreur Micro : {e}")

elif text_input:
    # Sinon on prend le texte
    final_user_input = text_input
    
if final_user_input:
    # 1. On affiche et sauvegarde le message USER
    st.chat_message("user").markdown(final_user_input)
    st.session_state.messages.append(HumanMessage(content=final_user_input))

    # 2. LOGIQUE D'ADAPTATION (THE STYLIST)
    style_instruction = ""
    if handicap_mode == "FALC (Facile à Lire)":
        style_instruction = "RÉPONDS EN FALC (Facile à Lire et à Comprendre) : Phrases courtes. Mots simples. Pas de jargon."
    elif handicap_mode == "TDAH (Focus & Gras)":
        style_instruction = "ADAPTATION TDAH : Mets en **GRAS** les concepts clés. Structure aérée. Va droit au but."
    elif handicap_mode == "Déficience Visuelle (Descriptif)":
        style_instruction = "ADAPTATION VISUELLE : Décris ce qui est visuel. Sois très explicite."
    
    # 3. APPEL AU CERVEAU
    with st.spinner(f"Analyse & Adaptation ({handicap_mode})..."):
        # Injection du style
        system_prompt = SystemMessage(content=f"INSTRUCTION DE STYLE : {style_instruction}")
        input_messages = [system_prompt] + st.session_state.messages
        
        # Le Cerveau réfléchit
        result = brain.invoke({"messages": input_messages})
        ai_response = result["messages"][-1]
        
        # Récupération des sources (Hack MVP)
        from rag_tool import retrieve_context_documents
        sources = retrieve_context_documents(final_user_input)

    # 4. AFFICHAGE DE LA RÉPONSE (Une seule fois !)
    st.chat_message("assistant").markdown(ai_response.content)
    
    # 5. AFFICHAGE DES SOURCES
    if sources:
        with st.expander("📚 Sources officielles utilisées"):
            for doc in sources:
                source_name = doc.metadata.get('source', 'Inconnu').split('/')[-1]
                page_num = doc.metadata.get('page', '?')
                st.caption(f"📄 **{source_name}** (Page {page_num})")
                st.text(doc.page_content[:150] + "...")

    # 6. SAUVEGARDE EN MÉMOIRE
    st.session_state.messages.append(ai_response)

    # 7. GÉNÉRATION AUDIO (TTS)
    client = OpenAI()
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=ai_response.content[:4096] 
        )
        audio_file = "speech.mp3"
        response.stream_to_file(audio_file)
        st.audio(audio_file, format="audio/mp3", start_time=0)
    except Exception as e:
        st.warning(f"Audio non disponible : {e}")