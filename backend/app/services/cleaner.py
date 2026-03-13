import re

def clean_wiki_evidence(text: str) -> str:
    if not text:
        return ""

    cleaned = text
    cleaned = re.sub(r"==.*?==", " ", cleaned)
    cleaned = re.sub(r"\{\{.*?\}\}", " ", cleaned)
    cleaned = re.sub(r"<.*?>", " ", cleaned)
    cleaned = re.sub(r"&[a-z0-9]+;", " ", cleaned)
    cleaned = re.sub(r"\[\[(File|Category|Image):[^\]]+\]\]", " ", cleaned)
    cleaned = re.sub(r"\[[^\]]*\]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned