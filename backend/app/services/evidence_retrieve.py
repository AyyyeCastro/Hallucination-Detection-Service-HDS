import re
from typing import Dict, Optional
from app.services.media_search import search_wikipedia
from app.services.media_content import get_page_extract
from app.services.query_helper import build_search_query, build_subject_query, check_query_quality

STOPWORDS = {
    "was", "is", "were", "are", "in", "on", "at", "of", "the", "a", "an",
    "born", "approximately", "went", "ago", "and", "with", "from", "by",
    "to", "his", "her", "their", "it", "that", "which", "who", "as",
    "for", "has", "had", "been", "about", "around", "during", "before", "after"
}

MIN_TITLE_OVERLAP = 1


def normalize_words(text: str) -> set[str]:
    words = re.findall(r"\b\w+\b", text.lower())
    return {word for word in words if word not in STOPWORDS}


def score_candidate_title(claim: str, title: str) -> int:
    claim_words = normalize_words(claim)
    title_words = normalize_words(title)

    overlap = len(claim_words & title_words)
    title_lower = title.lower()
    claim_lower = claim.lower()
    bonus = 3 if title_lower in claim_lower else 0
    return overlap + bonus


def choose_best_result(claim: str, search_results: list[dict]) -> dict:
    return max(search_results, key=lambda result: score_candidate_title(claim, result["title"]))


def _response(claim: str, search_query: Optional[str], subject_query: Optional[str], retrieval_status: str,
              grounding_status: str, retrieval_strategy: str, page_title=None, evidence_text=None,
              candidates=None, title_score: int = 0) -> Dict:
    return {
        "claim": claim,
        "search_query": search_query,
        "subject_search_query": subject_query,
        "page_title": page_title,
        "evidence_text": evidence_text,
        "candidates": candidates or [],
        "retrieval_status": retrieval_status,
        "grounding_status": grounding_status,
        "retrieval_strategy": retrieval_strategy,
        "title_score": title_score,
    }


def _search_and_extract(claim: str, query: str, subject_query: Optional[str], grounding_status: str,
                        strategy: str) -> Dict:
    if check_query_quality(query):
        return _response(claim, query, subject_query, "low_signal_query", grounding_status, strategy)

    search_results = search_wikipedia(query, limit=12)
    if not search_results:
        return _response(claim, query, subject_query, "no_search_results", grounding_status, strategy)

    best_result = choose_best_result(claim, search_results)
    page_title = best_result["title"]
    title_score = score_candidate_title(claim, page_title)

    if title_score < MIN_TITLE_OVERLAP:
        return _response(
            claim, query, subject_query, "weak_title_match", grounding_status, strategy,
            page_title=page_title, candidates=[result["title"] for result in search_results], title_score=title_score
        )

    extract = get_page_extract(page_title)
    if not extract or not extract.strip():
        return _response(
            claim, query, subject_query, "no_page_extract", grounding_status, strategy,
            page_title=page_title, candidates=[result["title"] for result in search_results], title_score=title_score
        )

    return _response(
        claim, query, subject_query, "ok", grounding_status, strategy,
        page_title=page_title,
        evidence_text=extract,
        candidates=[result["title"] for result in search_results],
        title_score=title_score,
    )


def get_claim_evidence(claim: str) -> Dict:
    subject_query = build_subject_query(claim)
    claim_query = build_search_query(claim)

    if subject_query:
        subject_result = _search_and_extract(
            claim=claim,
            query=subject_query,
            subject_query=subject_query,
            grounding_status="subject_grounded",
            strategy="subject_first",
        )
        if subject_result["retrieval_status"] == "ok":
            return subject_result

    fallback_result = _search_and_extract(
        claim=claim,
        query=claim_query,
        subject_query=subject_query,
        grounding_status="subject_grounded" if subject_query else "ungrounded",
        strategy="claim_fallback",
    )

    # Prefer a successful fallback over a failed subject-first result.
    if fallback_result["retrieval_status"] == "ok":
        return fallback_result

    # Otherwise, if subject-first existed, keep the stronger diagnostic unless it was missing.
    if subject_query:
        return subject_result

    return fallback_result
