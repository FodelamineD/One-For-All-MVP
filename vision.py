import base64
from openai import OpenAI
import streamlit as st

def analyze_image(uploaded_file):
    """
    Envoie une image à GPT-4o pour analyse.
    """
    client = OpenAI()
    
    # 1. Encodage de l'image en Base64 (Format que GPT comprend)
    # On lit les bytes du fichier uploadé
    bytes_data = uploaded_file.getvalue()
    base64_image = base64.b64encode(bytes_data).decode('utf-8')

    # 2. Appel API (Mode Vision)
    response = client.chat.completions.create(
        model="gpt-4o", # Le seul modèle qui voit bien
        messages=[
            {
                "role": "system",
                "content": "Tu es un assistant administratif qui aide les personnes handicapées. Ton but est de LIRE ce document, de le RÉSUMER simplement, et d'expliquer ce qu'il faut faire (Actions)."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyse ce document administratif. De quoi s'agit-il ?"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        },
                    },
                ],
            }
        ],
        max_tokens=500
    )

    return response.choices[0].message.content