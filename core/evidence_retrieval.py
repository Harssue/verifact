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
    # Default to no domain restriction unless explicitly requested in claim text.
    
    # 1. OPTIONAL: Check if the user specified a specific source in the claim (e.g., "according to reuters...")
    domain_filter = ""
    # Normalize claim for case-insensitive keyword matching.
    claim_lower = claim.lower()
    # Route query to Reuters if user preference is present in claim text.
    if "reuters" in claim_lower:
        domain_filter = "site:reuters.com"
    # Route query to BBC if claim references BBC.
    elif "bbc" in claim_lower:
        domain_filter = "site:bbc.com"
    # Route query to Bloomberg when requested.
    elif "bloomberg" in claim_lower:
        domain_filter = "site:bloomberg.com"
        
    # 2. DETECT LATEST NEWS: If claim contains dates or time-sensitive words, prefer Web Search.
    # Start with conservative assumption that claim is not time-sensitive.
    is_recent_news = False
    
    # Compute dynamic year tokens for recency detection.
    current_year = str(datetime.datetime.now().year)
    last_year = str(datetime.datetime.now().year - 1)
    
    # Keywords likely indicating rapidly changing or current events.
    time_keywords = [
        "today", "yesterday", "latest", "recent", "breaking", "as of", "now", 
        current_year, last_year, "january", "february", "march", "april", "may", "june", 
        "july", "august", "september", "october", "november", "december"
    ]
    # Mark claim as recent news if any recency token is present.
    for kw in time_keywords:
        if kw in claim_lower:
            is_recent_news = True
            break
    
    # 3. Try Wikipedia First (Unless they specifically asked for a news domain OR it is recent news)
    # Wikipedia works best for stable encyclopedic claims.
    if not domain_filter and not is_recent_news:
        try:
            # Build a simple keyword query from informative words.
            words = claim.split()
            keywords = " ".join([w for w in words if len(w) > 3])
            # Fall back to full claim if short-word filter removes everything.
            if not keywords:
                keywords = claim
            
            # Search for up to two likely matching pages.
            search_results = wikipedia.search(keywords, results=2)
            if search_results:
                # Pick top title and attempt summary extraction.
                page_title = search_results[0]
                try:
                    # Return concise summary as evidence text.
                    summary = wikipedia.summary(page_title, sentences=2, auto_suggest=False)
                    return summary, f"Wikipedia: {page_title}"
                except wikipedia.exceptions.DisambiguationError as e:
                    # Use first disambiguation option if title is ambiguous.
                    page_title = e.options[0]
                    summary = wikipedia.summary(page_title, sentences=2, auto_suggest=False)
                    return summary, f"Wikipedia: {page_title}"
                except wikipedia.exceptions.PageError:
                    # Continue to web fallback if selected page does not exist.
                    pass
        except Exception as e:
            # Avoid crashing request flow on retrieval issues.
            print(f"Wikipedia search failed: {e}")

    # 4. Fallback or News Preference: DuckDuckGo Web Search
    # This grabs the top text snippets from open web results, which is excellent for breaking news!
    try:
        # Include optional domain filter directly in search query string.
        query = claim if not domain_filter else f"{domain_filter} {claim}"
        
        # Run text search and fetch a small set of top results.
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
                    
            # Sort domain names for deterministic output ordering.
            source_list = ", ".join(sorted(domains)) if domains else "unknown"
            return evidence, f"Web Search ({source_list})"
            
    except Exception as e:
        # Log web fallback exceptions without interrupting caller logic.
        print(f"Web Search fallback failed: {e}")
        
    # Return explicit empty evidence when all retrieval paths fail.
    return "", "None"
