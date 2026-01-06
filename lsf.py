# lsf.py - Version "Liens Robustes"

LSF_DICTIONARY = {
    # BONJOUR (Waving hand simple)
    "bonjour": "https://media.giphy.com/media/dzaUX7CAG0Ihi/giphy.gif",
    "salut": "https://media.giphy.com/media/dzaUX7CAG0Ihi/giphy.gif",
    
# ARGENT (Lien Donald Duck - Plus stable)
    "argent": "https://media.giphy.com/media/xTiTnqUxyWbsAXq7Ju/giphy.gif",
    "payer": "https://media.giphy.com/media/xTiTnqUxyWbsAXq7Ju/giphy.gif",
    "aah": "https://media.giphy.com/media/xTiTnqUxyWbsAXq7Ju/giphy.gif",
    
    # MAISON (House)
    "maison": "https://media.giphy.com/media/3o6Mb9OEV5Dbd5EwTu/giphy.gif",
    "mdph": "https://media.giphy.com/media/3o6Mb9OEV5Dbd5EwTu/giphy.gif",
    
    # AIDER (Help sign)
    "aider": "https://media.giphy.com/media/8Y5tBwbAxP3lpMq4jr/giphy.gif",
    "aide": "https://media.giphy.com/media/8Y5tBwbAxP3lpMq4jr/giphy.gif",
    
    # MERCI
    "merci": "https://media.giphy.com/media/osjgQPWRx3cac/giphy.gif",
    
    # OUI / NON
    "oui": "https://media.giphy.com/media/111ebonMs90YLu/giphy.gif",
    "non": "https://media.giphy.com/media/gnE4FF7Cf9rlS/giphy.gif"
}

def get_lsf_matches(text):
    found = []
    # Nettoyage
    clean_text = text.lower().replace(".", " ").replace(",", " ").replace("'", " ")
    tokens = clean_text.split()
    
    for word in tokens:
        root_word = word.rstrip('s') 
        if root_word in LSF_DICTIONARY:
            found.append((root_word, LSF_DICTIONARY[root_word]))
            
    return list(set(found))