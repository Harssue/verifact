import nltk

# Ensure the punkt tokenizer is downloaded
try:
    # Check for sentence tokenizer assets used by sent_tokenize.
    nltk.data.find('tokenizers/punkt')
    # Newer NLTK versions may separate punkt tab data.
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    # Download tokenization model if it is missing locally.
    nltk.download('punkt')
    # Download punkt tab artifact when required by installed NLTK.
    nltk.download('punkt_tab')

import re

def extract_claims(text: str) -> list[str]:
    """
    Breaks a paragraph of text into atomic sentences (claims).
    """
    # Return no claims for empty or whitespace-only inputs.
    if not text or not text.strip():
        return []
    
    # Use NLTK's sentence tokenizer
    # Split paragraph into sentence candidates first.
    sentences = nltk.sent_tokenize(text)
    
    # Collect normalized final claims.
    claims = []
    
    # Process each tokenized sentence independently.
    for s in sentences:
        # Remove surrounding spaces for clean output.
        s = s.strip()
        # Skip accidental empty fragments.
        if not s:
            continue
            
        # Optional: heuristic split for the exam example:
        # "Albert Einstein was born in Germany and discovered gravity."
        # If one sentence joins two facts with 'and', attempt splitting.
        if " and " in s.lower():
            # Basic split on 'and'
            # Split once heuristically by conjunction.
            parts = re.split(r'\s+and\s+', s, flags=re.IGNORECASE)
            # Handle only simple two-part conjunctions.
            if len(parts) == 2:
                # Break first part into words to infer probable subject.
                words_part1 = parts[0].split()
                # If part 1 has a clear subject (first 2 words)
                # Require enough tokens before we try subject carry-forward.
                if len(words_part1) > 2:
                    # Use first two words as lightweight subject proxy.
                    subject = " ".join(words_part1[:2])
                    # First claim keeps left side unchanged.
                    claim1 = parts[0]
                    # Second claim prepends inferred subject to right side.
                    claim2 = subject + " " + parts[1]
                    
                    # Clean punctuation
                    # Normalize trailing periods consistently for UI display.
                    if claim1.endswith('.'): claim1 = claim1[:-1]
                    if not claim2.endswith('.'): claim2 += '.'
                    if not claim1.endswith('.'): claim1 += '.'
                    
                    # Store both split claims.
                    claims.append(claim1.strip())
                    claims.append(claim2.strip())
                    # Move to next sentence because split was successful.
                    continue
                    
        # Keep original sentence when no split heuristic applies.
        claims.append(s)
        
    # Return finalized list of extracted claims.
    return claims
