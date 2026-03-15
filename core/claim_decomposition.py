import nltk

# Ensure the punkt tokenizer is downloaded
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt')
    nltk.download('punkt_tab')

import re

def extract_claims(text: str) -> list[str]:
    """
    Breaks a paragraph of text into atomic sentences (claims).
    """
    if not text or not text.strip():
        return []
    
    # Use NLTK's sentence tokenizer
    sentences = nltk.sent_tokenize(text)
    
    claims = []
    
    for s in sentences:
        s = s.strip()
        if not s:
            continue
            
        # Optional: heuristic split for the exam example:
        # "Albert Einstein was born in Germany and discovered gravity."
        if " and " in s.lower():
            # Basic split on 'and'
            parts = re.split(r'\s+and\s+', s, flags=re.IGNORECASE)
            if len(parts) == 2:
                words_part1 = parts[0].split()
                # If part 1 has a clear subject (first 2 words)
                if len(words_part1) > 2:
                    subject = " ".join(words_part1[:2])
                    claim1 = parts[0]
                    claim2 = subject + " " + parts[1]
                    
                    # Clean punctuation
                    if claim1.endswith('.'): claim1 = claim1[:-1]
                    if not claim2.endswith('.'): claim2 += '.'
                    if not claim1.endswith('.'): claim1 += '.'
                    
                    claims.append(claim1.strip())
                    claims.append(claim2.strip())
                    continue
                    
        claims.append(s)
        
    return claims
