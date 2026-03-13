from app.services.claim_extractor import extract_claims
from app.services.context_helper import claim_context
from app.services.claim_verify import verify_claim
from app.services.results import total_summary, claim_summaries


def analyze_document(text: str) -> dict:
    extracted_claims = extract_claims(text)
    contextualized_claims = claim_context(extracted_claims)

    results = []

    for claim_data in contextualized_claims:
        original_claim = claim_data["original_claim"]
        context_based_claim = claim_data["context_based_claim"]

        verification_result = verify_claim(original_claim, context_based_claim)

        claim_result = claim_summaries(
            original_claim=original_claim,
            context_based_claim=context_based_claim,
            verification_result=verification_result
        )

        results.append(claim_result)

    summary = total_summary(results)

    return {
        "claims": results,
        "summary": summary
    }
    