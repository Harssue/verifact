import re


# ============================================================================
# PATTERN DEFINITIONS FOR DIFFERENT PII CATEGORIES
# ============================================================================

# Match candidate card-like numbers including optional spaces/hyphens.
CARD_CANDIDATE_PATTERN = re.compile(r"\b(?:\d[ -]*?){13,19}\b")

# ============================================================================
# DIRECT IDENTIFIERS: Government IDs, Financial Info, Medical/Health Info,
# Biometric Data, Login Credentials, Contact & Name Information
# ============================================================================
DIRECT_IDENTIFIERS = [
    # GOVERNMENT ID NUMBERS
    # US SSN formats: 123-45-6789 / 123 45 6789 / 123456789
    (r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b", "[REDACTED_SSN]"),
    # Tax ID / EIN (Employer Identification Number): XX-XXXXXXX
    (r"\b(tax\s*id|ein|tin|taxpayer\s*id)\s*[:#-]?\s*\d{2}-?\d{7}\b", "[REDACTED_TAX_ID]"),
    # Aadhaar (India) - unique national ID: XXXX XXXX XXXX
    (r"\b(aadhaar|aadhar)\s*(number|no\.?|#)?\s*[:#-]?\s*\d{4}\s?\d{4}\s?\d{4}\b", "[REDACTED_GOVT_ID]"),
    # Passport and driver's license with explicit context
    (r"\b(passport|driver'?s?\s*license|dl\s*no\.?|license\s*no\.?)\s*[:#-]?\s*[A-Za-z0-9-]{5,20}\b", "[REDACTED_GOVT_ID]"),
    
    # FULL NAMES (Direct identifier, especially when combined with other data)
    (r"\b[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b", "[REDACTED_NAME]"),
    
    # FINANCIAL INFORMATION
    # Credit card numbers (13-19 digits with optional spaces/hyphens)
    (r"\b(?:\d[ -]*?){13,19}\b", "[REDACTED_CREDIT_CARD]"),
    # Bank account numbers with explicit context
    (r"\b(account\s*(?:number|no\.?|#)?|iban|swift|ifsc|sort\s*code)\s*[:#-]?\s*[A-Za-z0-9-]{8,34}\b", "[REDACTED_ACCOUNT_NUMBER]"),
    # Salary/wage information explicitly labeled
    (r"\b(salary|wage|income|commission|bonus)\s*[:#-]?\s*\$?\\d{1,3}(?:,\\d{3})*(?:\\.\\d{2})?\b", "[REDACTED_SALARY]"),
    # Credit score indicators
    (r"\b(credit\s*score|fico\s*score|credit\s*rating)\s*[:#-]?\s*\d{3}\b", "[REDACTED_CREDIT_SCORE]"),
    
    # MEDICAL/HEALTH INFORMATION
    # Health insurance information with explicit context
    (r"\b(health\s*insurance|policy|insurance\s*id|member\s*id|group\s*number)\s*[:#-]?\s*[A-Za-z0-9-]{5,20}\b", "[REDACTED_INSURANCE_ID]"),
    # Medical record identifiers: MRN, EHR ID, Patient ID, Health ID
    (r"\b(medical\s*record\s*(?:number|no\.?|#)?|mrn|ehr\s*id|patient\s*id|health\s*id)\s*[:#-]?\s*[A-Za-z0-9-]{3,20}\b", "[REDACTED_MEDICAL_RECORD]"),
    
    # BIOMETRIC DATA
    # Fingerprint, facial recognition, iris scans, handwriting samples
    (r"\b(fingerprint|biometric\s*(?:template|record|data)?|retina|iris\s*scan|retinal\s*scan|face(?:ial)?\s*(?:scan|print|image|photo|recognition)|handwriting\s*sample)\b", "[REDACTED_BIOMETRIC]"),
    # Biometric ID codes: FPS-2024-001-XXXXX format
    (r"\b[A-Z]{2,4}-\d{4}-\d{3,4}-[A-Za-z0-9]{6,12}\b", "[REDACTED_BIOMETRIC]"),
    
    # LOGIN CREDENTIALS
    # Username:Password patterns - explicit credentials
    (r"\b(username|user\s*name|login|uid)\s*[:#-]?\s*[A-Za-z0-9._@-]{3,30}\s+(?:password|pwd|pass)\s*[:#-]?\s*\S{3,}\b", "[REDACTED_CREDENTIALS]"),
    # Security questions and answers
    (r"\b(security\s*question|secret\s*question|security\s*answer)\s*[:#-]?\s*[^\n]{5,100}\b", "[REDACTED_SECURITY_ANSWER]"),
    # API keys, tokens, secrets
    (r"\b(api\s*key|token|bearer|secret\s*key)\s*[:#-]?\s*[A-Za-z0-9_-]{20,}\b", "[REDACTED_API_KEY]"),
    
    # CONTACT INFORMATION  
    # Phone numbers: multiple formats - 7-digit (555-0199), 10-digit (555-123-4567), international (+1-555-123-4567)
    (r"\b(?:\+\d{1,3}[-.\s]?)?(?:\(?\d{0,3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b", "[REDACTED_PHONE]"),
    # Patient/Reference IDs that directly identify
    (r"\b(ref|reference|patient\s*ref)\s*[:#-]?\s*[A-Za-z0-9]{1,10}\b", "[REDACTED_PATIENT_REF]"),
]

# ============================================================================
# INDIRECT IDENTIFIERS: Contact Info, Personal Characteristics, Digital IDs,
# Professional Details, Location Data (Quasi-Identifiers)
# ============================================================================
INDIRECT_IDENTIFIERS = [
    # CONTACT INFORMATION
    # Email addresses: user@domain.com
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[REDACTED_EMAIL]"),
    # Mailing addresses (common patterns)
    (r"\b\d+\s+[A-Za-z\s.,-]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Circle|Cir|Way|Plaza|Pl|Square|Sq)\b", "[REDACTED_ADDRESS]"),
    
    # PERSONAL CHARACTERISTICS
    # Date of birth patterns: various formats (MM/DD/YYYY, DD-MM-YYYY, etc.)
    (r"\b(dob|date\s*of\s*birth|birth\s*date|born)\s*[:#-]?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b", r"\1: [REDACTED_DOB]"),
    # Age indicators
    (r"\b(age|years?\s*old|year-old)\s*[:#-]?\s*\d{1,3}\b", "[REDACTED_AGE]"),
    # Gender indicators - be more precise to avoid false positives
    (r"\b(?:gender|sex)\s*[:#-]?\s*(?:male|female|m|f|non-binary|other)(?:\s|[,.]|$)", "[REDACTED_GENDER]"),
    # Race/ethnicity indicators
    (r"\b(race|ethnicity|ethnic|ancestry)\s*[:#-]?\s*(caucasian|african|asian|hispanic|latino|native|american|indigenous|mixed|white|black|brown|asian|pacific|middle\s*eastern)\b", r"\1: [REDACTED_RACE]"),
    # Religion indicators
    (r"\b(religion|religious|faith|belief)\s*[:#-]?\s*(christian|muslim|jewish|hindu|buddhist|sikh|atheist|agnostic|orthodox|catholic|protestant)\b", r"\1: [REDACTED_RELIGION]"),
    # Place of birth
    (r"\b(place\s*of\s*birth|birthplace|born\s*in|origin)\s*[:#-]?\s*[A-Za-z\s,.-]{5,50}\b", "[REDACTED_PLACE_OF_BIRTH]"),
    # Mother's maiden name (commonly overlooked)
    (r"\b(mother'?s?\s*maiden\s*name|maternal\s*(surname|last\s*name))\s*[:#-]?\s*[A-Za-z\s-]{3,30}\b", "[REDACTED_MAIDEN_NAME]"),
    
    # DIGITAL IDENTIFIERS
    # IP addresses (IPv4)
    (r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b", "[REDACTED_IP_ADDRESS]"),
    # MAC addresses: XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX
    (r"\b(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})\b", "[REDACTED_MAC_ADDRESS]"),
    # Device IDs, Cookie IDs, Browser fingerprints
    (r"\b(device\s*id|device\s*identifier|cookie\s*id|browser\s*fingerprint|fingerprint\s*id)\s*[:#-]?\s*[A-Za-z0-9_-]{20,}\b", "[REDACTED_DEVICE_ID]"),
    
    # PROFESSIONAL DETAILS
    # Employee ID / Staff ID
    (r"\b(employee\s*id|staff\s*id|emp\s*no\.?|personnel\s*number)\s*[:#-]?\s*[A-Za-z0-9-]{3,15}\b", "[REDACTED_EMPLOYEE_ID]"),
    # Job title
    (r"\b(job\s*title|position|role|occupation)\s*[:#-]?\s*[A-Za-z\s]{3,50}\b", "[REDACTED_JOB_TITLE]"),
    # Previous employer
    (r"\b(previous\s*employer|prior\s*employer|last\s*employer|former\s*employer)\s*[:#-]?\s*[A-Za-z\s&.,-]{3,50}\b", "[REDACTED_EMPLOYER]"),
    # Company/Organization names (when linked with personal info)
    (r"\b(company|organization|employer|worked\s*at|employed\s*at)\s*[:#-]?\s*[A-Za-z\s&.,-]{3,50}\b", "[REDACTED_COMPANY]"),
    
    # LOCATION DATA
    # ZIP codes: 5-digit US format
    (r"\b\d{5}\b(?!=)", "[REDACTED_ZIPCODE]"),
    # ZIP+4 format
    (r"\b\d{5}[-]\d{4}\b", "[REDACTED_ZIPCODE]"),
    # GPS coordinates: latitude, longitude
    (r"\b(latitude|lng|lon|longitude|gps|coordinates)\s*[:#-]?\s*[-+]?\d{1,3}\.\d{2,10}\b", "[REDACTED_GPS_COORDINATE]"),
    # City/State patterns
    (r"\b(city|state|province|country)\s*[:#-]?\s*[A-Za-z\s]{3,50}\b", "[REDACTED_LOCATION]"),
]

# ============================================================================
# SENSITIVE PII: Medical Records, Bank Accounts, Biometric Data
# (Information that causes severe harm if disclosed)
# ============================================================================
SENSITIVE_PII = [
    # MEDICAL RECORDS
    # Health insurance information
    (r"\b(health\s*insurance|policy|insurance)\s*(?:id)??\s*[:#-]?\s*[A-Za-z0-9-]{5,20}\b", "[REDACTED_INSURANCE_ID]"),
    # Insurance ID standalone: BLUE-123456, etc.
    (r"\b[A-Z]+-?[0-9]{6,}\b", "[REDACTED_INSURANCE_ID]"),
    # Medical record identifiers: MRN, EHR ID, Patient ID, Health ID
    (r"\b(medical\s*record\s*(?:number|no\.?|#)?|mrn|ehr\s*id|patient\s*id|health\s*id)\s*[:#-]?\s*[A-Za-z0-9-]{3,20}\b", "[REDACTED_MEDICAL_RECORD]"),
    # Labeled medical narratives with more flexible patterns
    (r"\b(diagnosis|medical\s*history|chief\s*complaint|prescription|treatment\s*plan|lab\s*result[s]?|clinical\s*note[s]?|symptom[s]?|medication)\s*[:#-]?\s*[A-Za-z0-9\s',.-]{3,200}\b", "[REDACTED_MEDICAL_RECORD]"),
    # Medical conditions explicitly stated in records
    (r"\b(condition|disease|disorder|illness|syndrome)\s*[:#-]?\s*[A-Za-z\s',-]{5,50}\b", "[REDACTED_MEDICAL_CONDITION]"),
    
    # BIOMETRIC DATA
    # Fingerprints, facial recognition, iris scans
    (r"\b(fingerprint|biometric\s*template|retina|iris\s*scan|retinal\s*scan|face(?:ial)?\s*(?:scan|print|image|photo|recognition)|handwriting\s*sample)\b", "[REDACTED_BIOMETRIC]"),
    # Biometric ID patterns
    (r"\b[A-Z]{2,4}-\d{4}-\d{3,4}-[A-Za-z0-9]{6,12}\b", "[REDACTED_BIOMETRIC]"),
    
    # BANK ACCOUNT NUMBERS (distinct from general financial)
    # Structured bank account patterns
    (r"\b(account\s*(?:number|no\.?|#)?|iban|swift|ifsc|sort\s*code)\s*[:#-]?\s*[A-Za-z0-9-]{8,34}\b", "[REDACTED_ACCOUNT_NUMBER]"),
    
    # PHOTOGRAPHS/VIDEOS (commonly overlooked)
    # References to visual biometric data
    (r"\b(photograph|photo(?:graph)?|video|image|facial\s*image|picture|snapshot|frame)\s*(?:id|ref(?:erence)?|no\.?|#)?\s*[:#-]?\s*[A-Za-z0-9_-]{5,}\b", "[REDACTED_VISUAL_BIOMETRIC]"),
    
    # VEHICLES (commonly overlooked)
    # VIN - Vehicle Identification Number (17 characters)
    (r"\b(vin|vehicle\s*(?:identification|id|number))\s*[:#-]?\s*[A-HJ-NPR-Z0-9]{17}\b", "[REDACTED_VIN]"),
    # License plate numbers
    (r"\b(license\s*plate|plate\s*number|tag)\s*[:#-]?\s*[A-Z0-9]{2,8}\b", "[REDACTED_LICENSE_PLATE]"),
    # Motorcycle/vehicle model with explicit ID
    (r"\b(vehicle|car|motorcycle|truck)\s*(?:model|reg(?:istration)?|number)\s*[:#-]?\s*[A-Za-z0-9-]{5,30}\b", "[REDACTED_VEHICLE_ID]"),
]


# ============================================================================
# HELPER FUNCTIONS FOR PII REDACTION
# ============================================================================


def _passes_luhn(number: str) -> bool:
    """Validate card-like numeric strings to reduce false positive masking."""
    # Keep only digits so separators do not affect Luhn validation.
    digits = [int(ch) for ch in number if ch.isdigit()]
    # Card numbers are generally between 13 and 19 digits.
    if len(digits) < 13 or len(digits) > 19:
        return False

    # Compute checksum as defined by the Luhn algorithm.
    checksum = 0
    # Parity controls which digit positions are doubled.
    parity = len(digits) % 2
    # Iterate through normalized digits and accumulate checksum.
    for idx, digit in enumerate(digits):
        # Double every second digit according to parity.
        if idx % 2 == parity:
            digit *= 2
            # Reduce values above 9 by subtracting 9.
            if digit > 9:
                digit -= 9
        checksum += digit
    # Number is valid only when checksum is divisible by 10.
    return checksum % 10 == 0


def _mask_financial_numbers(text: str) -> str:
    """Redact credit card numbers and bank account identifiers."""
    # Redact card numbers only when they pass Luhn validation.
    def replace_card(match: re.Match) -> str:
        # Extract full matched candidate token.
        candidate = match.group(0)
        # Replace only real card numbers to avoid over-redaction.
        if _passes_luhn(candidate):
            return "[REDACTED_FINANCIAL_ACCOUNT]"
        # Preserve non-card numeric strings.
        return candidate

    # Run replacement callback over all card-like candidates.
    text = CARD_CANDIDATE_PATTERN.sub(replace_card, text)

    # Redact account numbers when context explicitly indicates bank/account data.
    bank_account_pattern = re.compile(
        r"\b(account\s*(number|no\.?|#)?|iban|swift|ifsc)\s*[:#-]?\s*[A-Za-z0-9-]{8,34}\b",
        re.IGNORECASE,
    )
    # Redact contextual account identifiers.
    return bank_account_pattern.sub("[REDACTED_FINANCIAL_ACCOUNT]", text)


def _apply_patterns(text: str, patterns: list) -> str:
    """
    Apply a list of regex patterns for redaction.
    
    Args:
        text: Input text to redact.
        patterns: List of (pattern, replacement) tuples.
    
    Returns:
        Text with patterns applied. Most patterns are case-insensitive for keywords,
        but some (like names) remain case-sensitive for accuracy.
    """
    # Apply each redaction rule. Most use IGNORECASE for keywords, but patterns
    # with specific case requirements (like proper names) are case-sensitive.
    for pattern, replacement in patterns:
        # Don't apply IGNORECASE to patterns designed for proper names or case-sensitive data
        if "REDACTED_NAME" in replacement:
            # Names are case-sensitive - only match Capitalized words
            text = re.sub(pattern, replacement, text)
        else:
            # All other patterns: apply case-insensitive for keywords/labels
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    # Return text after all patterns have been applied.
    return text


# ============================================================================
# CONTEXT-AWARE REDACTION FUNCTIONS
# ============================================================================


def anonymize_direct_identifiers(text: str) -> str:
    """
    Redact direct identifiers that uniquely identify an individual.
    
    Includes: SSN, Aadhaar, passport, driver's license, medical/patient IDs.
    """
    # Start with direct identifier patterns.
    text = _apply_patterns(text, DIRECT_IDENTIFIERS)
    # All direct identifiers are also sensitive, include biometric/medical redaction.
    text = _apply_patterns(text, SENSITIVE_PII)
    # Mask financial account numbers (part of sensitive data).
    text = _mask_financial_numbers(text)
    return text


def anonymize_indirect_identifiers(text: str) -> str:
    """
    Redact indirect identifiers that, when combined, can identify someone.
    
    Includes: Gender, race, date of birth, place of birth, zip code, age.
    This is typically used alongside direct identifier redaction.
    """
    # Apply each indirect identifier pattern using regex substitution.
    text = _apply_patterns(text, INDIRECT_IDENTIFIERS)
    return text


def anonymize_sensitive_pii(text: str) -> str:
    """
    Redact sensitive PII including medical records, biometric data, and financial info.
    
    Note: This is a legacy function for backward compatibility.
    Use anonymize_for_general_verification() or anonymize_for_ehr_lookup() instead.
    """
    # Apply direct identifier patterns.
    text = _apply_patterns(text, DIRECT_IDENTIFIERS)
    # Apply sensitive PII patterns separately.
    text = _apply_patterns(text, SENSITIVE_PII)
    # Apply specialized financial masking pass after general PII patterns.
    return _mask_financial_numbers(text)


def anonymize_for_general_verification(text: str) -> str:
    """
    Redact PII for general fact verification context.
    
    Redacts:
    - Direct Identifiers (SSN, passport, driver's license, unique IDs)
    - Sensitive PII (medical records, financial accounts, biometric data)
    
    Preserves:
    - Indirect Identifiers (gender, race, DOB, zip, place of birth, age)
      These are often contextual information in fact verification.
    
    Args:
        text: Input text containing potential PII.
    
    Returns:
        Text with direct and sensitive identifiers redacted.
    """
    # Apply direct identifier patterns first.
    text = _apply_patterns(text, DIRECT_IDENTIFIERS)
    # Then apply sensitive PII patterns.
    text = _apply_patterns(text, SENSITIVE_PII)
    # Finally apply financial masking (part of sensitive data).
    text = _mask_financial_numbers(text)
    return text


def anonymize_for_ehr_lookup(text: str) -> str:
    """
    Redact PII for Electronic Health Records (EHR) lookups.
    
    Redacts:
    - Direct Identifiers (SSN, passport, driver's license, unique IDs)
    - Indirect Identifiers (gender, race, DOB, zip, place of birth, age)
    - Sensitive PII (medical records, financial accounts, biometric data)
    
    Args:
        text: Input text from EHR or patient data containing all categories of PII.
    
    Returns:
        Fully anonymized text safe for EHR processing and external APIs.
    """
    # Apply direct identifier patterns first.
    text = _apply_patterns(text, DIRECT_IDENTIFIERS)
    # Then apply indirect identifier patterns.
    text = _apply_patterns(text, INDIRECT_IDENTIFIERS)
    # Then apply sensitive PII patterns.
    text = _apply_patterns(text, SENSITIVE_PII)
    # Finally apply financial masking (part of sensitive data).
    text = _mask_financial_numbers(text)
    return text


# ============================================================================
# HEALTHCARE-SPECIFIC REDACTION
# ============================================================================


def redact_healthcare_data(text: str) -> str:
    """
    Redact self-referential sensitive health conditions as sensitive medical record data.
    
    Identifies first-person descriptions of sensitive medical conditions
    and redacts them to protect patient privacy.
    """
    # Medical terms considered sensitive in first-person context.
    sensitive_medical_terms = [
        "hiv",
        "cancer",
        "diabetes",
        "syphilis",
        "tumor",
        "depression",
        "schizophrenia",
        "pregnancy",
        "abortion",
        "hepatitis",
        "stroke",
        "heart disease",
    ]

    # Prefixes that indicate the writer is describing their own condition.
    first_person_prefixes = r"\b(my|i have|i had|i was diagnosed with|my diagnosis of|treating my|my condition is)\s+"

    # Redact only when both first-person context and sensitive term appear.
    for term in sensitive_medical_terms:
        pattern = re.compile(first_person_prefixes + re.escape(term) + r"\b", re.IGNORECASE)
        text = pattern.sub(r"\1 [REDACTED_MEDICAL_RECORD]", text)

    # Return text with contextual healthcare redactions applied.
    return text


# ============================================================================
# COMPLIANCE AND LEGACY FUNCTIONS
# ============================================================================


def process_dpdp_compliance(text: str) -> str:
    """
    Apply sensitive PII redaction required for compliant processing (DPDP Act compliance).
    
    Uses anonymize_for_general_verification() internally since it's the standard
    approach for general fact-checking scenarios.
    """
    # First remove direct personal identifiers and document numbers.
    text = anonymize_for_general_verification(text)
    # Then redact self-referential sensitive medical condition mentions.
    text = redact_healthcare_data(text)
    # Return sanitized text safe for external processing.
    return text
