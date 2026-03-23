import re

def anonymize_pii(text: str) -> str:
    """
    Implements Data Minimization and Privacy by Design (IT Act 2000, GDPR, DPDP 2022).
    Before transferring data outside India (to HuggingFace APIs), we must redact 
    Sensitive Personal Data (PII) such as emails, phone numbers, and identifying codes.
    """
    # Redact Email Addresses
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    text = re.sub(email_pattern, '[REDACTED_EMAIL]', text)
    
    # Redact Indian Phone Numbers (e.g., +91 9876543210 or 9876543210)
    phone_pattern = r'(\+91[\-\s]?)?[6-9]\d{9}'
    text = re.sub(phone_pattern, '[REDACTED_PHONE]', text)
    
    # Redact Aadhar Numbers (12 digits, optional spaces)
    aadhar_pattern = r'\b\d{4}\s?\d{4}\s?\d{4}\b'
    text = re.sub(aadhar_pattern, '[REDACTED_AADHAR]', text)
    
    return text

def redact_healthcare_data(text: str) -> str:
    """
    Implements Unit V: Healthcare Data Protection & SeHA / NeHA protocols.
    Data Minimization should only apply to the USER'S personal data, not public figures 
    being fact-checked. We use regex to only mask diseases when preceded by 
    first-person possessive phrases (e.g. 'my cancer', 'I have diabetes').
    """
    sensitive_medical_terms = [
        "hiv", "cancer", "diabetes", "syphilis", "tumor", 
        "depression", "schizophrenia", "pregnancy", "abortion"
    ]
    
    # We build a pattern that looks for "I have ", "my ", "diagnosed me with ", etc.
    # followed unconditionally by the medical term.
    first_person_prefixes = r'\b(my|i have|i was diagnosed with|my diagnosis of|treating my)\s+'
    
    for term in sensitive_medical_terms:
        # Combine the prefix and the term
        pattern = re.compile(first_person_prefixes + term + r'\b', re.IGNORECASE)
        # Replace the entire match (e.g., "my cancer") with a generic tag
        text = pattern.sub(r'\1 [PROTECTED_HEALTH_DATA]', text)
        
    return text

def process_dpdp_compliance(text: str) -> str:
    """
    Applies all required DPDP 2022 and GDPR protections.
    """
    text = anonymize_pii(text)
    text = redact_healthcare_data(text)
    return text
