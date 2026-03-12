import requests
from typing import List, Dict

WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"

HEADERS = {
    "User-Agent": "HallucinationDetectionService/0.1 (Andrew Castro; https://andrewcastro.dev)"
}


def search_wikipedia(query: str, limit: int = 5) -> List[Dict]:
    params = {
        "action": "query",
        "list": "search",
        "format": "json",
        "srlimit": limit,
        "srsearch": query,
        "srwhat": "text",
    }

    response = requests.get(
        WIKIPEDIA_API_URL,
        params=params,
        headers=HEADERS,
        timeout=10,
    )
    response.raise_for_status()

    data = response.json()
    return data.get("query", {}).get("search", [])