# lsf.py - Dictionnaire corrigé (Liens stables)

LSF_DICTIONARY = {
    # BONJOUR (Signe de la main classique)
    "bonjour": "https://media.tenor.com/gUACOHDzdJ0AAAAC/hello-sign-language.gif",
    
    # ARGENT (Frotter les doigts)
    "argent": "https://media.tenor.com/n1j-rM6Jb7kAAAAC/pay-me-money.gif",
    "payer": "https://media.tenor.com/n1j-rM6Jb7kAAAAC/pay-me-money.gif",
    "aah": "https://media.tenor.com/n1j-rM6Jb7kAAAAC/pay-me-money.gif", # On triche pour la démo
    
    # MAISON (Toit avec les mains)
    "maison": "https://media.tenor.com/bQPz3YlKzLAAAAAC/house-home.gif",
    "mdph": "https://media.tenor.com/bQPz3YlKzLAAAAAC/house-home.gif", # On associe MDPH à Maison
    
    # MERCI (Main au menton)
    "merci": "https://media.tenor.com/Qk2q5q4Wq1QAAAAC/thank-you-sign.gif",
    
    # AIDER (Pouce levé sur paume)
    "aider": "https://media.tenor.com/5S9s1Su1lAAAAAAC/help-asl.gif",
    "aide": "https://media.tenor.com/5S9s1Su1lAAAAAAC/help-asl.gif",
    
    # OUI / NON
    "oui": "https://media.tenor.com/5JJz5f3Xwz0AAAAC/yes-nod.gif",
    "non": "https://media.tenor.com/1M1S7K_7Gz0AAAAC/no-nope.gif"
}

def get_lsf_matches(text):
    """
    Scanne le texte et retourne la liste des (mot, url) trouvés.
    """
    found = []
    # Nettoyage agressif pour trouver les mots clés
    clean_text = text.lower().replace(".", " ").replace(",", " ").replace("'", " ")
    tokens = clean_text.split()
    
    for word in tokens:
        # On garde le mot racine (ex: 'maisons' -> 'maison')
        root_word = word.rstrip('s') 
        
        if root_word in LSF_DICTIONARY:
            found.append((root_word, LSF_DICTIONARY[root_word]))
            
    # On dédoublonne pour ne pas afficher 3 fois le même GIF
    return list(set(found))