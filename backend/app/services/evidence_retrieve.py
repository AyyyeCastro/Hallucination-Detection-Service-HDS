from typing import Dict, Optional
from app.services.media_search import search_wikipedia
from app.services.media_content import get_page_extract


def retrieve_evidence_for_claim(claim: str) -> Dict:
    search_results = search_wikipedia(claim, limit=5)

    if not search_results:
        return {
            "claim": claim,
            "page_title": None,
            "evidence_text": None,
            "candidates": [],
        }

    best_result = search_results[0]
    page_title = best_result["title"]
    extract = get_page_extract(page_title)

    return {
        "claim": claim,
        "page_title": page_title,
        "evidence_text": extract,
        "candidates": [result["title"] for result in search_results],
    }
