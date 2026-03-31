import re


# Match candidate card-like numbers including optional spaces/hyphens.
CARD_CANDIDATE_PATTERN = re.compile(r"\b(?:\d[ -]*?){13,19}\b")


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


def anonymize_sensitive_pii(text: str) -> str:
    """
    Redact direct/sensitive PII before sending text to external APIs.

    Allowed (not redacted): non-sensitive/indirect PII such as name, email,
    phone, address, DOB, ZIP, IP, and demographic attributes.
    """
    # Regex replacement rules for direct/sensitive identifiers.
    patterns = [
        # US SSN formats: 123-45-6789 / 123 45 6789 / 123456789
        (r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b", "[REDACTED_SSN]"),
        # Aadhaar redaction only when explicit context is present.
        (r"\b(aadhaar|aadhar)\s*(number|no\.?|#)?\s*[:#-]?\s*\d{4}\s?\d{4}\s?\d{4}\b", "[REDACTED_GOVT_ID]"),
        # Passport / driver's license numbers when a keyword indicates document context.
        (
            r"\b(passport|driver'?s?\s*license|dl\s*no\.?|license\s*no\.?)\s*[:#-]?\s*[A-Za-z0-9-]{5,20}\b",
            "[REDACTED_GOVT_ID]",
        ),
        # Biometric references and identifiers (including biometric ID codes like FPS-XXXX-XXX-XXXXXX).
        (
            r"\b(fingerprint|retina|iris\s*scan|face\s*(scan|print|image|photo)|biometric\s*(record|template|id)?)\b",
            "[REDACTED_BIOMETRIC]",
        ),
        # Biometric ID codes: patterns like FPS-2024-001-XXX or similar alphanumeric sequences
        (r"\b[A-Z]{2,4}-\d{4}-\d{3,4}-[A-Za-z0-9]{6,12}\b", "[REDACTED_BIOMETRIC]"),
        # Structured medical record identifiers.
        (
            r"\b(medical\s*record\s*(number|no\.?|#)?|mrn|ehr\s*id|patient\s*id)\s*[:#-]?\s*[A-Za-z0-9-]{3,20}\b",
            "[REDACTED_MEDICAL_RECORD]",
        ),
        # Labeled medical narratives often contain full record content.
        (
            r"\b(diagnosis|medical\s*history|chief\s*complaint|prescription|treatment\s*plan|lab\s*result[s]?)\s*:\s*[^\n]+",
            "[REDACTED_MEDICAL_RECORD]",
        ),
    ]

    # Apply each redaction rule case-insensitively.
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # Apply specialized financial masking pass after general PII patterns.
    return _mask_financial_numbers(text)


def redact_healthcare_data(text: str) -> str:
    """
    Redact self-referential health conditions as sensitive medical record data.
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


def process_dpdp_compliance(text: str) -> str:
    """Apply sensitive PII redaction required for compliant processing."""
    # First remove direct personal identifiers and document numbers.
    text = anonymize_sensitive_pii(text)
    # Then redact self-referential sensitive medical condition mentions.
    text = redact_healthcare_data(text)
    # Return sanitized text safe for external processing.
    return text
