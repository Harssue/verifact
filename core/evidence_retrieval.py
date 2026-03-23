import wikipedia
import re
from ddgs import DDGS
import datetime

def retrieve_evidence(claim: str) -> tuple[str, str]:
    """
    Searches Wikipedia for evidence. If not found, falls back to DuckDuckGo Search.
    Extracts web snippets as evidence.
    Returns (evidence_text, source_name).
    """
    
    # 1. OPTIONAL: Check if the user specified a specific source in the claim (e.g., "according to reuters...")
    domain_filter = ""
    claim_lower = claim.lower()
    if "reuters" in claim_lower:
        domain_filter = "site:reuters.com"
    elif "bbc" in claim_lower:
        domain_filter = "site:bbc.com"
    elif "bloomberg" in claim_lower:
        domain_filter = "site:bloomberg.com"
        
    # 2. DETECT LATEST NEWS: If claim contains dates or time-sensitive words, prefer Web Search.
    is_recent_news = False
    
    current_year = str(datetime.datetime.now().year)
    last_year = str(datetime.datetime.now().year - 1)
    
    time_keywords = [
        "today", "yesterday", "latest", "recent", "breaking", "as of", "now", 
        current_year, last_year, "january", "february", "march", "april", "may", "june", 
        "july", "august", "september", "october", "november", "december"
    ]
    for kw in time_keywords:
        if kw in claim_lower:
            is_recent_news = True
            break
    
    # 3. Try Wikipedia First (Unless they specifically asked for a news domain OR it is recent news)
    if not domain_filter and not is_recent_news:
        try:
            words = claim.split()
            keywords = " ".join([w for w in words if len(w) > 3])
            if not keywords:
                keywords = claim
            
            search_results = wikipedia.search(keywords, results=2)
            if search_results:
                page_title = search_results[0]
                try:
                    summary = wikipedia.summary(page_title, sentences=2, auto_suggest=False)
                    return summary, f"Wikipedia: {page_title}"
                except wikipedia.exceptions.DisambiguationError as e:
                    page_title = e.options[0]
                    summary = wikipedia.summary(page_title, sentences=2, auto_suggest=False)
                    return summary, f"Wikipedia: {page_title}"
                except wikipedia.exceptions.PageError:
                    pass
        except Exception as e:
            print(f"Wikipedia search failed: {e}")

    # 4. Fallback or News Preference: DuckDuckGo Web Search
    # This grabs the top text snippets from open web results, which is excellent for breaking news!
    try:
        query = claim if not domain_filter else f"{domain_filter} {claim}"
        
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=3)
            
        if results:
            # Combine the text snippets from the top 3 search results
            evidence = " ".join([res.get('body', '') for res in results])
            
            # Grab the domain names of the sources
            domains = set()
            for res in results:
                href = res.get('href', '')
                if href:
                    # extract domain roughly (e.g. https://www.bbc.com/... -> www.bbc.com)
                    domain = href.split('/')[2] if len(href.split('/')) > 2 else href
                    domains.add(domain)
                    
            source_list = ", ".join(domains)
            return evidence, f"Web Search ({source_list})"
            
    except Exception as e:
        print(f"Web Search fallback failed: {e}")
        
    return "", "None"
