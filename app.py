import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from openai import OpenAI
from graph import app as brain
from utils import to_bionic_reading
from lsf import get_lsf_matches
from rag_tool import retrieve_context_documents
import os
from vision import analyze_image

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="One For All", page_icon="🛡️", layout="wide")

# CSS HACK (Gras Rouge + Style Audio)
st.markdown(
    """
    <style>
    b { color: #D90429 !important; font-weight: 900 !important; }
    .stAudio { margin-top: 10px; }
    </style>
    """,
    unsafe_allow_html=True
)

# BOOTLOADER
if not os.path.exists("./chroma_db"):
    st.warning("⚠️ Base de données introuvable. Lancement de l'ingestion...")
    import ingest
    try:
        ingest.ingest_documents()
        st.success("✅ Mémoire construite !")
        st.rerun()
    except Exception as e:
        st.error(f"Erreur Ingestion : {e}")
        st.stop()

# 3. INITIALISATION MÉMOIRE
if "messages" not in st.session_state:
    st.session_state.messages = [
        AIMessage(content="Bonjour ! Je suis l'assistant One For All. Je peux lire, voir et écouter. Comment puis-je vous aider ?")
    ]

# 2. SIDEBAR : OUTILS & CONFIG
with st.sidebar:
    st.image("https://img.icons8.com/color/96/accessibility2.png", width=80)
    
    # ONGLETS
    tab_vocal, tab_vision = st.tabs(["🎙️ Vocal", "📸 Vision"])
    
    # --- ONGLET 1 : VOCAL ---
    with tab_vocal:
        st.caption("Posez votre question à la voix :")
        audio_value = st.audio_input("Enregistrer", key="micro_sidebar")

    # --- ONGLET 2 : VISION (CORRECTIF LOGIQUE ICI) ---
    with tab_vision:
        st.caption("Analysez un courrier :")
        uploaded_file = st.file_uploader("Choisir une image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
        
        if uploaded_file:
            if st.button("👁️ Décrypter", use_container_width=True):
                with st.spinner("Analyse GPT-4o..."):
                    try:
                        # 1. Analyse
                        analysis = analyze_image(uploaded_file)
                        
                        # 2. SIMULATION D'UNE CONVERSATION LOGIQUE
                        # On ajoute d'abord la QUESTION de l'utilisateur (virtuelle)
                        st.session_state.messages.append(HumanMessage(content="📸 J'ai scanné ce document. Peux-tu l'analyser ?"))
                        
                        # On ajoute ensuite la RÉPONSE de l'IA
                        st.session_state.messages.append(AIMessage(content=f"📄 **Analyse du document :**\n\n{analysis}"))
                        
                        # 3. On recharge pour afficher le tout dans le bon ordre
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur : {e}")

    st.markdown("---")
    
    # --- REGLAGES ---
    st.header("⚙️ Profil")
    handicap_mode = st.radio(
        "Type d'adaptation :",
        [
            "Standard", 
            "FALC (Facile à Lire)", 
            "TDAH (Focus & Gras)", 
            "Déficience Visuelle (Descriptif)",
            "Sourd (LSF & Visuel)"
        ]
    )
    st.caption(f"Mode : **{handicap_mode}**")

# 4. AFFICHAGE DE L'HISTORIQUE (AVEC FILTRE RÉTROACTIF)
for message in st.session_state.messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
            
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            content_to_display = message.content
            
            # Application du Bionic Reading sur l'historique
            if handicap_mode == "TDAH (Focus & Gras)":
                content_to_display = to_bionic_reading(content_to_display)
                st.markdown("""<style>b { color: #D90429 !important; font-weight: 900 !important; }</style>""", unsafe_allow_html=True)
                st.markdown(content_to_display, unsafe_allow_html=True)
            else:
                st.markdown(content_to_display, unsafe_allow_html=True)

# 5. GESTION DES ENTRÉES (Micro OU Clavier)
text_input = st.chat_input("Écrivez votre question ici...")
final_user_input = None

if audio_value:
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
    final_user_input = text_input

# --- 6. LE CŒUR DU SYSTÈME (Nouvelle entrée Texte/Audio) ---
# --- 6. LE CŒUR DU SYSTÈME ---
if final_user_input:
    # 🛡️ ANTI-DOUBLON (DEDUP)
    # On récupère le dernier message envoyé par l'HUMAIN dans l'historique
    last_human_msg = None
    for msg in reversed(st.session_state.messages):
        if isinstance(msg, HumanMessage):
            last_human_msg = msg.content
            break
            
    # Si le message actuel est IDENTIQUE au dernier message humain, on stop tout.
    # C'est juste un rafraîchissement de page, pas une nouvelle question.
    if last_human_msg == final_user_input:
        # On ne fait RIEN, on laisse le script continuer sans ré-ajouter le message
        pass
        
    else:
        # C'est un VRAI nouveau message -> ON TRAITE
        
        # A. Affichage USER
        st.session_state.messages.append(HumanMessage(content=final_user_input))
        with st.chat_message("user"):
            st.markdown(final_user_input)

        # B. DÉFINITION DU STYLE
        style_instruction = ""
        if handicap_mode == "FALC (Facile à Lire)":
            style_instruction = "RÉPONDS EN FALC. Phrases courtes. Listes à puces. Vocabulaire simple."
        elif handicap_mode == "TDAH (Focus & Gras)":
            style_instruction = "ADAPTATION TDAH : Phrases courtes. AUCUN GRAS NI MARKDOWN. Texte brut uniquement."
        elif handicap_mode == "Déficience Visuelle (Descriptif)":
            style_instruction = "ADAPTATION VISUELLE : Décris le visuel. Sois explicite."
        elif handicap_mode == "Sourd (LSF & Visuel)":
            style_instruction = "ADAPTATION SOURD : Français simple (Sujet-Verbe-Complément). Pas de métaphores."

       
        # C. REFLEXION
    with st.spinner(f"Analyse & Adaptation ({handicap_mode})..."):
        # 🔥 ON AJOUTE LA CONSCIENCE DE L'INTERFACE ICI
        interface_context = """
        CONTEXTE INTERFACE :
        Tu es l'assistant "One For All" intégré dans une application.
        - Tu as un onglet '📸 Vision' dans la barre latérale (à gauche) capable de lire/scanner des courriers via OCR.
        - Tu as un onglet '🎙️ Vocal' pour l'audio.
        
        RÈGLE DE COMPORTEMENT :
        Si l'utilisateur dit "Je veux te montrer un fichier" ou "Lis ce document", NE DIS PAS que tu ne peux pas.
        DIS-LUI : "Allez dans l'onglet 📸 Vision à gauche et chargez votre image."
        """
        
        # On fusionne le contexte technique + le style (TDAH/FALC)
        full_system_prompt = f"{interface_context}\n\nINSTRUCTION DE STYLE : {style_instruction}"
        
        system_msg = SystemMessage(content=full_system_prompt)
        input_messages = [system_msg] + st.session_state.messages
        
        # Le Graphe réfléchit
        result = brain.invoke({"messages": input_messages})
        ai_response = result["messages"][-1]
        
        sources = retrieve_context_documents(final_user_input)

        # D. AFFICHAGE RÉPONSE
        display_text = ai_response.content
        
        with st.chat_message("assistant"):
            if handicap_mode == "TDAH (Focus & Gras)":
                display_text = to_bionic_reading(display_text)
                st.caption("⚡ Bionic Reading (HTML Mode)")
                st.markdown(display_text, unsafe_allow_html=True)
            else:
                st.markdown(display_text)

        # E. EXTENSIONS (LSF / Sources)
        if handicap_mode == "Sourd (LSF & Visuel)":
            matches = get_lsf_matches(ai_response.content)
            if matches:
                with st.expander("👋 Traduction LSF (Mots-clés)", expanded=True):
                    cols = st.columns(3)
                    for i, (word, url) in enumerate(matches):
                        with cols[i % 3]:
                            st.image(url, use_container_width=True)
                            st.markdown(f"**{word.capitalize()}**")

        if sources:
            with st.expander("📚 Sources officielles"):
                for doc in sources:
                    name = doc.metadata.get('source', 'Doc').split('/')[-1]
                    st.caption(f"📄 {name}")

        # F. SAUVEGARDE & AUDIO
        st.session_state.messages.append(ai_response)

        if handicap_mode != "Sourd (LSF & Visuel)":
            client = OpenAI()
            try:
                tts = client.audio.speech.create(model="tts-1", voice="alloy", input=ai_response.content[:4096])
                tts.stream_to_file("speech.mp3")
                st.audio("speech.mp3", start_time=0)
            except:
                pass