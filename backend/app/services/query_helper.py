import re
from app.services.model_helper import spacy

nlp = spacy.load("en_core_web_sm")

ALLOWED_POS = {"PROPN", "NOUN", "ADJ", "NUM"}

LOW_SIGNAL_TERMS = {
    "famous", "known", "world", "understanding", "introduced",
    "achievement", "fundamentally", "altered", "made", "best"
}

def build_search_query(claim: str) -> str:
    doc = nlp(claim)
    terms = []

    for ent in doc.ents:
        if ent.label_ in {"PERSON", "ORG", "GPE", "EVENT", "DATE"}:
            terms.append(ent.text)

    for token in doc:
        if token.is_stop or token.is_punct:
            continue
        if token.pos_ not in ALLOWED_POS:
            continue

        text = token.text.strip()
        if not text:
            continue

        if text.lower() in LOW_SIGNAL_TERMS:
            continue

        terms.append(text)

    seen = set()
    deduped = []

    for term in terms:
        cleaned = re.sub(r"\s+", " ", term).strip()
        if cleaned and cleaned.lower() not in seen:
            deduped.append(cleaned)
            seen.add(cleaned.lower())

    return " ".join(deduped[:10])