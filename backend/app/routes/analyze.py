from fastapi import APIRouter
from app.models.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.claim_extractor import extract_claims
from app.services.claim_verify import verify_claim, verification_score

router = APIRouter()


@router.post("/", response_model=AnalyzeResponse)
def analyze_text(request: AnalyzeRequest):
    extracted_claims = extract_claims(request.text)

    results = []
    total_score = 0.0

    for claim in extracted_claims:
        verification_result = verify_claim(claim)

        results.append({
            "claim": claim,
            "score": verification_result["score"],
            "verification": verification_score(verification_result["score"]),
            "evidence": [verification_result["best_evidence"]] if verification_result["best_evidence"] else []
        })

        total_score += verification_result["score"]

    hallucination_score = 0.0
    if extracted_claims:
        average_support = total_score / len(extracted_claims)
        hallucination_score = 1 - average_support

    return {
        "claims": results,
        "hallucination_score": hallucination_score
    }