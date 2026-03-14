import re
from typing import Optional
from app.services.model_helper import nlp

NATIONALITY_WORDS = {
    "american", "mexican", "korean", "south korean", "north korean", "japanese", "chinese",
    "british", "french", "german", "italian", "canadian", "russian", "indian"
}

BIRTH_HINTS = {"born", "birthplace"}
DEATH_HINTS = {"died", "death", "place of death"}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _extract_entities(text: str, labels: set[str]) -> list[str]:
    doc = nlp(text)
    return [ent.text for ent in doc.ents if ent.label_ in labels]


def detect_contradiction(claim: str, evidence: str) -> Optional[str]:
    if not claim or not evidence:
        return None

    claim_lower = _normalize(claim)
    evidence_lower = _normalize(evidence)

    claim_gpes = _extract_entities(claim, {"GPE", "LOC"})
    evidence_gpes = _extract_entities(evidence, {"GPE", "LOC"})
    claim_dates = set(re.findall(r"\b(1[0-9]{3}|20[0-9]{2})\b", claim))
    evidence_dates = set(re.findall(r"\b(1[0-9]{3}|20[0-9]{2})\b", evidence))

    if any(hint in claim_lower for hint in BIRTH_HINTS) and claim_gpes and evidence_gpes:
        if not set(map(str.lower, claim_gpes)) & set(map(str.lower, evidence_gpes)):
            return "birthplace_mismatch"

    if any(hint in claim_lower for hint in DEATH_HINTS) and claim_gpes and evidence_gpes:
        if not set(map(str.lower, claim_gpes)) & set(map(str.lower, evidence_gpes)):
            return "deathplace_mismatch"

    if claim_dates and evidence_dates and not (claim_dates & evidence_dates):
        return "year_mismatch"

    claim_nationalities = {word for word in NATIONALITY_WORDS if word in claim_lower}
    evidence_nationalities = {word for word in NATIONALITY_WORDS if word in evidence_lower}
    if claim_nationalities and evidence_nationalities and not (claim_nationalities & evidence_nationalities):
        return "nationality_or_origin_mismatch"

    return None
