def _stable_sorted(values) -> list[str]:
    return sorted({str(v) for v in values}, key=lambda x: (len(x), x))


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

    matched_numbers = set()
    mismatched_numbers = set()

    matched_numbers |= (claim_years & evidence_years)
    matched_numbers |= (claim_millions & evidence_millions)
    matched_numbers |= (claim_numbers & evidence_numbers)

    mismatched_numbers |= (claim_years - evidence_years)
    mismatched_numbers |= (claim_millions - evidence_millions)
    mismatched_numbers |= (claim_numbers - evidence_numbers)

    # Never show the same numeric token as both matched and mismatched.
    mismatched_numbers -= matched_numbers

    return {
        "claim": original_claim,
        "context_based_claim": context_based_claim,
        "search_query": verification_result.get("search_query"),
        "subject_search_query": verification_result.get("subject_search_query"),
        "retrieval_status": verification_result.get("retrieval_status", "ok"),
        "grounding_status": verification_result.get("grounding_status", "ungrounded"),
        "retrieval_strategy": verification_result.get("retrieval_strategy", "claim_fallback"),
        "contradiction_reason": verification_result.get("contradiction_reason"),
        "score": verification_result.get("score", 0.0),
        "semantic_score": verification_result.get("semantic_score", 0.0),
        "verification": verification_result.get("verification", "Insufficient Evidence"),
        "evidence": [verification_result["best_evidence"]] if verification_result.get("best_evidence") else [],
        "page_title": verification_result.get("page_title"),
        "matched_numbers": _stable_sorted(matched_numbers),
        "mismatched_numbers": _stable_sorted(mismatched_numbers),
    }


def total_summary(results: list[dict]) -> dict:
    if not results:
        return {
            "claims_analyzed": 0,
            "overall_score": 0.0,
            "overall_verification": "Insufficient Evidence"
        }

    total_score = sum(result["score"] for result in results)
    overall_score = total_score / len(results)

    labels = [result.get("verification") for result in results]

    supported_count = sum(1 for label in labels if label == "Supported")
    contradicted_count = sum(1 for label in labels if label == "Contradicted")
    retrieval_failed_count = sum(1 for label in labels if label == "Retrieval Failed")

    if contradicted_count > 0:
        overall_verification = "Contradicted"
    elif all(label == "Retrieval Failed" for label in labels):
        overall_verification = "Retrieval Failed"
    elif (
        supported_count >= max(1, int(0.75 * len(results)))
        and retrieval_failed_count == 0
        and overall_score >= 0.6
    ):
        overall_verification = "Supported"
    else:
        overall_verification = "Insufficient Evidence"

    return {
        "claims_analyzed": len(results),
        "overall_score": overall_score,
        "overall_verification": overall_verification,
    }
