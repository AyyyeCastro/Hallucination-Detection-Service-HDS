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

def clean_LLM_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("“", "\"").replace("”", "\"").replace("’", "'")
    text = text.replace("—", " — ").replace("–", " – ")
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'(?:(?<=\s)|(?<=^)|(?<=[\.\,\;\:]))\+\d+\b', ' ', text)
    text = re.sub(r'\[\d+\]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text