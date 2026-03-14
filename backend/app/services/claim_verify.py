from app.services.evidence_retrieve import get_claim_evidence
from app.services.cleaner import clean_wiki_evidence
from app.services.text_chunker import text_chunker
from app.services.chunk_compare import find_best_match
from app.services.num_helper import compare_num_evidence
from app.services.verification_helper import detect_contradiction

LOW_SEMANTIC_THRESHOLD = 0.35
SUPPORTED_THRESHOLD = 0.72


def verify_claim(original_claim: str, context_based_claim: str) -> dict:
    retrieval = get_claim_evidence(context_based_claim)
    retrieval_status = retrieval.get("retrieval_status", "ok")

    raw_evidence_text = retrieval.get("evidence_text")
    cleaned_evidence_text = clean_wiki_evidence(raw_evidence_text) if raw_evidence_text else ""
    chunks = text_chunker(cleaned_evidence_text) if cleaned_evidence_text else []

    if retrieval_status == "ok" and not chunks:
        retrieval_status = "no_evidence_chunks"

    match = find_best_match(context_based_claim, chunks)
    if retrieval_status == "ok" and match["best_chunk"] is None:
        retrieval_status = "no_evidence_chunks"

    if retrieval_status == "ok" and match["score"] < LOW_SEMANTIC_THRESHOLD:
        retrieval_status = "low_semantic_match"

    best_evidence = match["best_chunk"]
    contradiction_reason = detect_contradiction(context_based_claim, best_evidence) if best_evidence else None
    fact_result = compare_num_evidence(context_based_claim, best_evidence) if best_evidence else {}

    adjusted_score = match["score"]
    if fact_result.get("year_match"):
        adjusted_score += 0.15
    if fact_result.get("million_match"):
        adjusted_score += 0.15
    elif fact_result.get("number_match"):
        adjusted_score += 0.05

    adjusted_score = max(0.0, min(adjusted_score, 1.0))

    if contradiction_reason:
        verification = "Contradicted"
        final_score = 0.0
    elif retrieval_status in {"low_signal_query", "no_search_results", "weak_title_match", "no_page_extract", "no_evidence_chunks"}:
        verification = "Retrieval Failed"
        final_score = adjusted_score
    elif adjusted_score >= SUPPORTED_THRESHOLD:
        verification = "Supported"
        final_score = adjusted_score
    else:
        verification = "Insufficient Evidence"
        final_score = adjusted_score

    return {
        "claim": original_claim,
        "context_based_claim": context_based_claim,
        "search_query": retrieval.get("search_query"),
        "subject_search_query": retrieval.get("subject_search_query"),
        "page_title": retrieval.get("page_title"),
        "candidates": retrieval.get("candidates", []),
        "best_evidence": best_evidence,
        "score": final_score,
        "semantic_score": match["score"],
        "fact_result": fact_result,
        "retrieval_status": retrieval_status,
        "grounding_status": retrieval.get("grounding_status", "ungrounded"),
        "retrieval_strategy": retrieval.get("retrieval_strategy", "claim_fallback"),
        "contradiction_reason": contradiction_reason,
        "verification": verification,
    }
