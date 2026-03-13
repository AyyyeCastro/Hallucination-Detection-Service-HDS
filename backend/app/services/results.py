from app.services.claim_verify import score_to_label


def claim_summaries(
    original_claim: str,
    context_based_claim: str,
    verification_result: dict
) -> dict:
    fact_result = verification_result.get("fact_result", {})

    claim_years = set(fact_result.get("claim_years", []))
    evidence_years = set(fact_result.get("evidence_years", []))
    claim_millions = set(fact_result.get("claim_millions", []))
    evidence_millions = set(fact_result.get("evidence_millions", []))
    claim_numbers = set(fact_result.get("claim_numbers", []))
    evidence_numbers = set(fact_result.get("evidence_numbers", []))

    matched_numbers = []
    mismatched_numbers = []

    matched_numbers.extend(list(claim_years & evidence_years))
    matched_numbers.extend(list(claim_millions & evidence_millions))
    matched_numbers.extend(list(claim_numbers & evidence_numbers))

    mismatched_numbers.extend(list(claim_years - evidence_years))
    mismatched_numbers.extend(list(claim_millions - evidence_millions))
    mismatched_numbers.extend(list(claim_numbers - evidence_numbers))

    return {
        "claim": original_claim,
        "context_based_claim": context_based_claim,
        "search_query": verification_result.get("search_query"),
        "score": verification_result["score"],
        "semantic_score": verification_result["semantic_score"],
        "verification": score_to_label(verification_result["score"]),
        "evidence": [verification_result["best_evidence"]] if verification_result["best_evidence"] else [],
        "page_title": verification_result["page_title"],
        "matched_numbers": matched_numbers,
        "mismatched_numbers": mismatched_numbers,
    }
    

def total_summary(results: list[dict]) -> dict:
    if not results:
        return {
            "claims_analyzed": 0,
            "overall_score": 0.0,
            "overall_verification": "Unfounded"
        }

    total_score = sum(result["score"] for result in results)
    overall_score = total_score / len(results)

    return {
        "claims_analyzed": len(results),
        "overall_score": overall_score,
        "overall_verification": score_to_label(overall_score)
    }