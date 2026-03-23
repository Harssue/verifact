import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from core.claim_decomposition import extract_claims
from core.evidence_retrieval import retrieve_evidence
from core.verification import verify_claim
from core.privacy_filter import process_dpdp_compliance
import pandas as pd

load_dotenv()

app = FastAPI(title="VeriFact System with DPDP Compliance")

# Ensure directories exist
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"results": None})

@app.post("/verify", response_class=HTMLResponse)
async def verify_text(
    request: Request, 
    user_text: str = Form(...),
# DPDP Requirement: Grounds for Processing Data (Requires Explicit User Consent)
    dpdp_consent: str = Form(None),
    patient_id: str = Form(None)
):
    if not dpdp_consent:
        return templates.TemplateResponse(request=request, name="index.html", context={
            "error_msg": "Under the DPDP Act 2022, you must grant consent to process your data.",
            "user_text": user_text
        })

    # DATA MINIMIZATION (UNIT V: Healthcare Data & Personal Data)
    # Mask PII and Health Data BEFORE sending outside India
    safe_text = process_dpdp_compliance(user_text)

    # 1. Decompose into claims (using the anonymized text)
    claims = extract_claims(safe_text)
    
    results = []
    
    # Check if a Patient ID was provided to query the local "Hospital Database"
    fetched_ehr_text = ""
    if patient_id and patient_id.strip():
        try:
            df = pd.read_csv("data/ehr_database.csv", dtype=str)
            patient_record = df[df["patient_id"] == patient_id.strip()]
            if not patient_record.empty:
                fetched_ehr_text = patient_record.iloc[0]["ehr_text"]
        except Exception as e:
            print(f"Database error: {e}")

    for claim in claims:
        # 2. Retrieve Evidence (If EHR is found in DB, use it as Ground Truth)
        if fetched_ehr_text:
            evidence = fetched_ehr_text
            source = f"Hospital Database (Patient ID: {patient_id.strip()})"
        else:
            evidence, source = retrieve_evidence(claim)
        
        # 3. Verify Claim
        if evidence:
            verdict, explanation = verify_claim(claim, evidence)
        else:
            verdict, explanation = "Not Enough Information", "Could not find relevant evidence."
        
        results.append({
            "claim": claim,
            "verdict": verdict,
            "explanation": explanation,
            "source": source
        })
        
    return templates.TemplateResponse(
        request=request, name="index.html", context={
        "user_text": user_text,
        "clean_text": safe_text, # Show them how we protected their data
        "results": results
    })

# UNIT-IV GDPR: Right to be Forgotten (Data Erasure)
@app.post("/right_to_be_forgotten", response_class=HTMLResponse)
async def erase_data(request: Request):
    # In a real database, we would drop the user's records here.
    return templates.TemplateResponse(request=request, name="index.html", context={
        "results": None,
        "info_msg": "Your data has been permanently erased from our systems in compliance with GDPR Art. 17 and DPDP 2022."
    })
