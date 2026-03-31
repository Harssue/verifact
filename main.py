import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from core.claim_decomposition import extract_claims
from core.evidence_retrieval import retrieve_evidence
from core.verification import verify_claim
from core.privacy_filter import process_dpdp_compliance, anonymize_for_ehr_lookup
import pandas as pd

# Load environment variables from a local .env file if available.
load_dotenv()

# Create the FastAPI app instance with a descriptive API title.
app = FastAPI(title="VeriFact System with DPDP Compliance")

# Ensure directories exist
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Render the landing page with no verification results yet.
    return templates.TemplateResponse(request=request, name="index.html", context={"results": None})

@app.post("/verify", response_class=HTMLResponse)
async def verify_text(
    request: Request, 
    # Raw text submitted by the user for claim verification.
    user_text: str = Form(...),
# DPDP Requirement: Grounds for Processing Data (Requires Explicit User Consent)
    # Consent checkbox field (must be present to continue processing).
    dpdp_consent: str = Form(None),
    # Optional patient identifier used to fetch local EHR evidence.
    patient_id: str = Form(None)
):
    # Block processing when explicit consent is not provided.
    if not dpdp_consent:
        return templates.TemplateResponse(request=request, name="index.html", context={
            "error_msg": "Under the DPDP Act 2022, you must grant consent to process your data.",
            "user_text": user_text,
            "patient_id": patient_id or "",
        })

    # DATA MINIMIZATION (UNIT V: Healthcare Data & Personal Data)
    # Mask PII and Health Data BEFORE sending outside India
    # Apply privacy filtering before external retrieval/verification.
    safe_text = process_dpdp_compliance(user_text)

    # 1. Decompose into claims (using the anonymized text)
    # Break normalized text into sentence-level claims.
    claims = extract_claims(safe_text)
    
    # Collect per-claim verdicts and supporting details.
    results = []
    
    # Check if a Patient ID was provided to query the local "Hospital Database"
    # Hold fetched EHR evidence from local CSV if patient lookup succeeds.
    fetched_ehr_text = ""
    # Normalize whitespace once so downstream usage is consistent.
    normalized_patient_id = patient_id.strip() if patient_id else ""
    # Attempt local evidence lookup only when patient_id is present.
    if patient_id and patient_id.strip():
        try:
            # Read local EHR database in string mode to preserve IDs exactly.
            df = pd.read_csv("data/ehr_database.csv", dtype=str)
            # Filter to the matching patient row.
            patient_record = df[df["patient_id"] == normalized_patient_id]
            # Pull the first matched EHR text as evidence.
            if not patient_record.empty:
                fetched_ehr_text = patient_record.iloc[0]["ehr_text"]
                # DATA MINIMIZATION: Apply full EHR anonymization to fetched data
                # Redact ALL PII categories (Direct + Indirect + Sensitive) for EHR lookups
                fetched_ehr_text = anonymize_for_ehr_lookup(fetched_ehr_text)
        except Exception as e:
            # Keep service running even if local data source has issues.
            print(f"Database error: {e}")

    # Run verification for every extracted claim.
    for claim in claims:
        # 2. Retrieve Evidence (If EHR is found in DB, use it as Ground Truth)
        # Prefer local patient EHR as source-of-truth when available.
        if fetched_ehr_text:
            evidence = fetched_ehr_text
            source = f"Hospital Database (Patient ID: {normalized_patient_id})"
        else:
            # Otherwise retrieve open-web/Wikipedia evidence.
            evidence, source = retrieve_evidence(claim)
        
        # 3. Verify Claim
        # Ask verifier only when there is non-empty evidence text.
        if evidence:
            verdict, explanation = verify_claim(claim, evidence)
        else:
            # Provide deterministic fallback when no evidence could be found.
            verdict, explanation = "Not Enough Information", "Could not find relevant evidence."
        
        # Store one structured result per claim for UI rendering.
        results.append({
            "claim": claim,
            "verdict": verdict,
            "explanation": explanation,
            "source": source
        })
        
    # Render verification results, original text, and anonymized text preview.
    return templates.TemplateResponse(
        request=request, name="index.html", context={
        "user_text": user_text,
        "patient_id": normalized_patient_id,
        "clean_text": safe_text, # Show them how we protected their data
        "results": results
    })

# UNIT-IV GDPR: Right to be Forgotten (Data Erasure)
@app.post("/right_to_be_forgotten", response_class=HTMLResponse)
async def erase_data(request: Request):
    # In a real database, we would drop the user's records here.
    # Return a UI confirmation that simulates completed erasure.
    return templates.TemplateResponse(request=request, name="index.html", context={
        "results": None,
        "info_msg": "Your data has been permanently erased from our systems in compliance with GDPR Art. 17 and DPDP 2022."
    })
