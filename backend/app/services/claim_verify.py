from app.services.evidence_retrieve import get_claim_evidence
from app.services.cleaner import clean_wiki_evidence
from app.services.text_chunker import text_chunker
from app.services.chunk_compare import find_best_match
from app.services.num_helper import compare_num_evidence


def verify_claim(original_claim: str, context_based_claim: str) -> dict:
    retrieval = get_claim_evidence(context_based_claim)

    raw_evidence_text = retrieval["evidence_text"]
    cleaned_evidence_text = clean_wiki_evidence(raw_evidence_text) if raw_evidence_text else ""

    chunks = text_chunker(cleaned_evidence_text) if cleaned_evidence_text else []
    match = find_best_match(context_based_claim, chunks)

    fact_result = compare_num_evidence(context_based_claim, match["best_chunk"]) if match["best_chunk"] else {}
    adjusted_score = match["score"]

    # claim_years = set(fact_result.get("claim_years", []))
    # evidence_years = set(fact_result.get("evidence_years", []))

    # claim_millions = set(fact_result.get("claim_millions", []))
    # evidence_millions = set(fact_result.get("evidence_millions", []))

    # claim_numbers = set(fact_result.get("claim_numbers", []))
    # evidence_numbers = set(fact_result.get("evidence_numbers", []))


    if fact_result.get("year_match"):
        adjusted_score += 0.15
    
    if fact_result.get("million_match"):
        adjusted_score += 0.15
    elif fact_result.get("number_match"):
        adjusted_score += 0.05

    # Not going to penalize in this iteration, just yet.
    # if claim_years and evidence_years and not fact_result.get("year_match"):
    #     adjusted_score -= 0.20
    
    # if claim_millions and evidence_millions and not fact_result.get("million_match"):
    #     adjusted_score -= 0.15
    # elif claim_numbers and evidence_numbers and not fact_result.get("number_match"):
    #     adjusted_score -= 0.08

    adjusted_score = max(0.0, min(adjusted_score, 1.0))

    return {
        "claim": original_claim,
        "context_based_claim": context_based_claim,
        "search_query": retrieval.get("search_query"),
        "page_title": retrieval["page_title"],
        "candidates": retrieval["candidates"],
        "best_evidence": match["best_chunk"],
        "score": adjusted_score,
        "semantic_score": match["score"],
        "fact_result": fact_result
    }


def score_to_label(score: float) -> str:
    if score >= 0.78:
        return "Verified"
    if score >= 0.65:
        return "Probable"
    if score >= 0.50:
        return "Questionable"
    return "Unfounded"

