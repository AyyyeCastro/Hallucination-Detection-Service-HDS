from app.services.evidence_retrieve import retrieve_evidence_for_claim
from app.services.text_chunker import text_chunker
from app.services.chunk_compare import find_best_match


def verify_claim(claim: str) -> dict:
    retrieval = retrieve_evidence_for_claim(claim)

    evidence_text = retrieval["evidence_text"]
    chunks = text_chunker(evidence_text) if evidence_text else []

    match = find_best_match(claim, chunks)

    return {
        "claim": claim,
        "page_title": retrieval["page_title"],
        "candidates": retrieval["candidates"],
        "best_evidence": match["best_chunk"],
        "score": match["score"]
    }

def verification_score(score: float) -> str:
    if score >= 0.85:
        return "has_verification"
    if score >= 0.50:
        return "little_verification"
    return "hallucination"