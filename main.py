import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from core.claim_decomposition import extract_claims
from core.evidence_retrieval import retrieve_evidence
from core.verification import verify_claim

load_dotenv()

app = FastAPI(title="VeriFact System")

# Ensure directories exist
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "results": None})

@app.post("/verify", response_class=HTMLResponse)
async def verify_text(request: Request, user_text: str = Form(...)):
    # 1. Decompose into claims
    claims = extract_claims(user_text)
    
    results = []
    
    for claim in claims:
        # 2. Retrieve Evidence
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
        
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "user_text": user_text,
        "results": results
    })
