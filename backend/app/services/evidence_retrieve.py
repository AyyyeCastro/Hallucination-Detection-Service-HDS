import re
from typing import Dict
from app.services.media_search import search_wikipedia
from app.services.media_content import get_page_extract
from app.services.query_helper import build_search_query

STOPWORDS = {
    "was", "is", "were", "are", "in", "on", "at", "of", "the", "a", "an",
    "born", "approximately", "went", "ago", "and", "with", "from", "by", 
    "to", "his", "her", "their", "it", "that", "which", "who", "as", 
    "for", "has", "had", "been", "about", "around", "during", "before", "after"
}

def normalize_words(text: str) -> set[str]:
    words = re.findall(r"\b\w+\b", text.lower())
    return {word for word in words if word not in STOPWORDS}

def score_candidate_title(claim: str, title: str) -> int:
    claim_words = normalize_words(claim)
    title_words = normalize_words(title)

    overlap = len(claim_words & title_words)
    title_lower = title.lower()
    claim_lower = claim.lower()

    bonus = 0
    if title_lower in claim_lower:
        bonus += 3

    return overlap + bonus

def choose_best_result(claim: str, search_results: list[dict]) -> dict:
    return max(search_results, key=lambda result: score_candidate_title(claim, result["title"]))

def get_claim_evidence(claim: str) -> Dict:
    query = build_search_query(claim)
    search_results = search_wikipedia(query, limit=5)

    if not search_results:
        return {
            "claim": claim,
            "page_title": None,
            "evidence_text": None,
            "candidates": [],
        }

    best_result = choose_best_result(claim, search_results)
    page_title = best_result["title"]
    extract = get_page_extract(page_title)

    return {
        "claim": claim,
        "search_query": query,
        "page_title": page_title,
        "evidence_text": extract,
        "candidates": [result["title"] for result in search_results],
    }