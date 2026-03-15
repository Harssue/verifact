import wikipedia
import re

def retrieve_evidence(claim: str) -> tuple[str, str]:
    """
    Searches Wikipedia for keywords in the claim and retrieves a summary as evidence.
    Returns (evidence_text, source_name).
    """
    try:
        # Extract potential keywords. A highly simplified approach: removing common stop words
        # In a real system, we might use NER or POS tagging.
        words = claim.split()
        keywords = " ".join([w for w in words if len(w) > 3])
        if not keywords:
            keywords = claim
            
        # Search for Wikipedia pages matching the keywords
        search_results = wikipedia.search(keywords, results=2)
        
        if search_results:
            page_title = search_results[0]
            try:
                # get a short summary (2 sentences)
                summary = wikipedia.summary(page_title, sentences=2, auto_suggest=False)
                return summary, f"Wikipedia: {page_title}"
            except wikipedia.exceptions.DisambiguationError as e:
                # If ambiguous, pick the first option
                page_title = e.options[0]
                summary = wikipedia.summary(page_title, sentences=2, auto_suggest=False)
                return summary, f"Wikipedia: {page_title}"
            except wikipedia.exceptions.PageError:
                pass
                
        return "", "None"
    except Exception as e:
        print(f"Error retrieving evidence: {e}")
        return "", "None"
