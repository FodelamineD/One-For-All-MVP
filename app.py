import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from graph import app as brain
from openai import OpenAI # On a besoin du client direct pour l'audio
from rag_tool import retrieve_context_documents
import streamlit as st
import os
from utils import to_bionic_reading
from lsf import get_lsf_matches
# ... tes autres imports ...


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

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="One For All", page_icon="♾️", layout="wide")
# CSS HACK : Renforce le gras pour le Bionic Reading
st.markdown(
    """
    <style>
    b {
        font-weight: 900 !important; /* Gras ultra-lourd */
        color: #FF4B4B; /* Optionnel : Met le début des mots en ROUGE Streamlit pour le test */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- SIDEBAR : CONFIGURATION UTILISATEUR ---
# --- SIDEBAR : CONFIGURATION & OUTILS ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/accessibility2.png", width=80)
    st.header("🎛️ Configuration")
    
    # 1. Choix du Handicap
    handicap_mode = st.radio(
        "Mode d'adaptation :",
        ["Standard", "FALC (Facile à Lire)", "TDAH (Focus & Gras)", "Déficience Visuelle (Descriptif)", "Sourd (LSF & Visuel)"]
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
    
# --- DÉCLENCHEMENT DU CERVEAU ---
if final_user_input:
    # 1. On affiche le message de l'UTILISATEUR
    st.chat_message("user").markdown(final_user_input)
    st.session_state.messages.append(HumanMessage(content=final_user_input))

    # 2. DÉFINITION DU STYLE (Consignes pour le cerveau)
    style_instruction = ""
    if handicap_mode == "FALC (Facile à Lire)":
        style_instruction = """
        RÉPONDS EN FALC.
        RÈGLE : Utilise des phrases courtes.
        Si procédure : [ ] Étape 1...
        """
    elif handicap_mode == "TDAH (Focus & Gras)":
        style_instruction = "ADAPTATION TDAH : Phrases courtes. AUCUN GRAS NI MARKDOWN. Texte brut uniquement."
    elif handicap_mode == "Déficience Visuelle (Descriptif)":
        style_instruction = "ADAPTATION VISUELLE : Décris le visuel. Sois explicite."
    elif handicap_mode == "Sourd (LSF & Visuel)":
        style_instruction = "ADAPTATION SOURD : Français simple (Sujet-Verbe-Complément). Pas de métaphores."

    # 3. LE CERVEAU RÉFLÉCHIT (Appel Backend)
    with st.spinner(f"Analyse & Adaptation ({handicap_mode})..."):
        # Prompt système temporaire
        system_prompt = SystemMessage(content=f"INSTRUCTION DE STYLE : {style_instruction}")
        input_messages = [system_prompt] + st.session_state.messages
        
        # Invocation LangGraph
        result = brain.invoke({"messages": input_messages})
        ai_response = result["messages"][-1] # <--- L'IA a répondu, la variable existe maintenant !
        
        # Récupération des sources (RAG)
        sources = retrieve_context_documents(final_user_input)

    # 4. AFFICHAGE DE LA RÉPONSE
    display_text = ai_response.content
    
    # A. Mode Bionic (HTML) - Seulement si TDAH
    if handicap_mode == "TDAH (Focus & Gras)":
        display_text = to_bionic_reading(display_text)
        st.markdown("""<style>b { color: #D90429 !important; font-weight: 900 !important; }</style>""", unsafe_allow_html=True)
        st.caption("⚡ Bionic Reading (Mode HTML)")
        st.chat_message("assistant").markdown(display_text, unsafe_allow_html=True)
    else:
        # B. Mode Standard (Pour tous les autres, y compris Sourds)
        st.chat_message("assistant").markdown(display_text)

    # 5. BONUS : LSF (Langue des Signes) - Seulement si Sourd
    if handicap_mode == "Sourd (LSF & Visuel)":
        matches = get_lsf_matches(ai_response.content)
        if matches:
            with st.expander("👋 Traduction LSF (Mots-clés)", expanded=True):
                cols = st.columns(3)
                for i, (word, url) in enumerate(matches):
                    with cols[i % 3]:
                        st.image(url, use_container_width=True)
                        st.markdown(f"**{word.capitalize()}**")
        else:
            st.info("👋 Aucun mot-clé LSF détecté.")

    # 6. BONUS : SOURCES (Pour tout le monde)
    if sources:
        with st.expander("📚 Sources officielles"):
            for doc in sources:
                name = doc.metadata.get('source', 'Doc').split('/')[-1]
                page = doc.metadata.get('page', '?')
                st.caption(f"📄 {name} (p.{page})")

    # 7. FINITION : SAUVEGARDE & AUDIO
    st.session_state.messages.append(ai_response)

    # Audio pour tout le monde SAUF les sourds (inutile)
    if handicap_mode != "Sourd (LSF & Visuel)":
        client = OpenAI()
        try:
            tts = client.audio.speech.create(model="tts-1", voice="alloy", input=ai_response.content[:4096])
            tts.stream_to_file("speech.mp3")
            st.audio("speech.mp3", start_time=0)
        except:
            pass
