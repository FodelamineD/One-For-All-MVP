import re

def to_bionic_reading(text):
    # D'abord, on nettoie le texte : on enlève le gras Markdown s'il y en a déjà
    clean_text = text.replace("**", "").replace("__", "")
    
    def process_word(match):
        word = match.group(0)
        length = len(word)
        
        # Mot court (< 3 lettres) -> Tout en gras
        if length <= 3:
            return f"<b>{word}</b>"
            
        # Mot long -> Moitié + 1 en gras
        bold_len = (length // 2) + 1
        return f"<b>{word[:bold_len]}</b>{word[bold_len:]}"

    # On applique la transfo sur les mots
    return re.sub(r'\b[a-zA-ZÀ-ÿ0-9]+\b', process_word, clean_text)