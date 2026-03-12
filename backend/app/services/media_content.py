import requests
from typing import Optional

WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"

HEADERS = {
    "User-Agent": "HallucinationDetectionService/0.1 (Andrew Castro; https://andrewcastro.dev)"
}

def get_page_extract(title: str, chars: int = 2000) -> Optional[str]:
    params = {
        "action": "query",
        "prop": "extracts",
        "format": "json",
        "titles": title,
        "explaintext": 1,
        "exchars": chars,
        "formatversion": 2,
    }

    response = requests.get(
        WIKIPEDIA_API_URL,
        params=params,
        headers=HEADERS,
        timeout=10,
    )
    response.raise_for_status()

    data = response.json()
    pages = data.get("query", {}).get("pages", [])

    if not pages:
        return None

    return pages[0].get("extract")