import re
from typing import Optional
from app.services.model_helper import nlp

ALLOWED_POS = {"PROPN", "NOUN", "ADJ", "NUM"}

ANCHOR_ENTITY_LABELS = {
    "PERSON", "ORG", "GPE", "LOC", "EVENT", "WORK_OF_ART",
    "NORP", "PRODUCT", "FAC"
}
DATE_ENTITY_LABELS = {"DATE"}

LOW_SIGNAL_TERMS = {
    "extremely", "highly", "truly", "really", "very", "quite",
    "completely", "absolutely", "basically", "actually", "simply",
    "fundamentally", "primarily", "essentially", "literally",
    "many", "several", "various", "numerous", "some", "few",
    "aspect", "factor", "element", "thing", "process", "approach",
    "variety", "collection", "amount", "level",
    "greatest", "significant", "important", "effective", "useful",
    "excellent", "amazing", "incredible", "outstanding", "worst",
    "perfect", "top", "leading", "popular",
    "recently", "currently", "previously", "initially", "finally",
    "meanwhile", "ongoing", "future", "modern", "traditional",
    "example", "sample", "definition", "overview", "summary",
    "instance", "detail", "information", "data", "brief",
    "roots", "conditions", "country", "government", "system", "period"
}

GENERIC_SUBJECT_HEADS = {
    "conditions", "condition", "country", "government", "system", "period",
    "approach", "method", "process", "thing", "factors", "roots", "year"
}

GENERIC_SUBJECT_PREFIXES = {
    "this", "that", "these", "those", "the", "a", "an"
}


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _dedupe_terms(terms: list[str]) -> list[str]:
    seen = set()
    deduped: list[str] = []
    for term in terms:
        cleaned = normalize_space(term)
        key = cleaned.lower()
        if cleaned and key not in seen:
            deduped.append(cleaned)
            seen.add(key)
    return deduped


def _is_low_value_subject(text: str) -> bool:
    if not text:
        return True

    words = [w.lower() for w in re.findall(r"\b[\w'-]+\b", text)]
    if not words:
        return True

    if len(words) <= 2 and all(w in GENERIC_SUBJECT_HEADS | GENERIC_SUBJECT_PREFIXES for w in words):
        return True

    if words[0] in GENERIC_SUBJECT_PREFIXES and len(words) <= 3:
        return True

    if words[-1] in GENERIC_SUBJECT_HEADS:
        return True

    return False


def _entity_priority(ent) -> tuple[int, int]:
    # higher is better
    label_rank = {
        "PERSON": 6,
        "WORK_OF_ART": 5,
        "EVENT": 5,
        "ORG": 4,
        "GPE": 4,
        "PRODUCT": 3,
        "FAC": 3,
        "NORP": 2,
        "LOC": 2,
    }
    return (label_rank.get(ent.label_, 0), len(ent.text.split()))


def extract_primary_subject(claim: str) -> Optional[str]:
    doc = nlp(claim)

    strong_entities = [ent for ent in doc.ents if ent.label_ in ANCHOR_ENTITY_LABELS]
    if strong_entities:
        strong_entities = sorted(strong_entities, key=_entity_priority, reverse=True)
        best = normalize_space(strong_entities[0].text)
        if not _is_low_value_subject(best):
            return best

    for token in doc:
        if token.dep_ in {"nsubj", "nsubjpass"}:
            if token.pos_ == "PRON":
                continue
            subtree = sorted(list(token.subtree), key=lambda t: t.i)
            subject_text = normalize_space(" ".join(t.text for t in subtree if not t.is_punct))
            if subject_text and not _is_low_value_subject(subject_text):
                return subject_text

    return None


def _get_date_terms(doc) -> list[str]:
    dates = []
    for ent in doc.ents:
        if ent.label_ == "DATE":
            dates.append(normalize_space(ent.text))
    return _dedupe_terms(dates)


def _covered_by_entity(token, entity_spans: list[tuple[int, int]]) -> bool:
    return any(start <= token.i < end for start, end in entity_spans)


def extract_relation_terms(claim: str, subject: str | None = None) -> list[str]:
    doc = nlp(claim)
    terms: list[str] = []

    quoted_phrases = re.findall(r'"([^"]+)"', claim)
    terms.extend(normalize_space(phrase) for phrase in quoted_phrases if normalize_space(phrase))

    subject_lower = subject.lower() if subject else None
    subject_tokens = set(subject_lower.split()) if subject_lower else set()

    entity_spans = [(ent.start, ent.end) for ent in doc.ents]

    # add entities first, including dates
    for ent in doc.ents:
        ent_text = normalize_space(ent.text)
        if not ent_text:
            continue
        if subject_lower and ent_text.lower() == subject_lower:
            continue
        if ent.label_ in DATE_ENTITY_LABELS | ANCHOR_ENTITY_LABELS:
            terms.append(ent_text)

    # add token-level terms, but skip tokens already covered by an entity span
    for token in doc:
        if token.is_stop or token.is_punct:
            continue
        if _covered_by_entity(token, entity_spans):
            continue
        if token.pos_ not in ALLOWED_POS and token.dep_ not in {"ROOT", "attr", "acomp", "oprd", "dobj", "pobj"}:
            continue

        text = normalize_space(token.lemma_ if token.pos_ in {"VERB", "AUX"} else token.text)
        if not text:
            continue

        lower = text.lower()
        if lower in LOW_SIGNAL_TERMS:
            continue
        if lower in subject_tokens:
            continue

        terms.append(text)

    return _dedupe_terms(terms)


def build_subject_query(claim: str) -> Optional[str]:
    doc = nlp(claim)
    subject = extract_primary_subject(claim)
    if not subject:
        return None

    pieces = [subject]

    # keep strongest date anchors with subject-first retrieval
    date_terms = _get_date_terms(doc)
    pieces.extend(date_terms[:2])

    # add one or two non-subject entity anchors if useful
    extra_entities = []
    for ent in doc.ents:
        ent_text = normalize_space(ent.text)
        if ent.label_ not in ANCHOR_ENTITY_LABELS:
            continue
        if ent_text.lower() == subject.lower():
            continue
        extra_entities.append(ent_text)

    pieces.extend(_dedupe_terms(extra_entities)[:2])

    return normalize_space(" ".join(_dedupe_terms(pieces)[:5]))


def build_search_query(claim: str) -> str:
    subject = extract_primary_subject(claim)
    relation_terms = extract_relation_terms(claim, subject)

    pieces: list[str] = []
    if subject:
        pieces.append(subject)

    pieces.extend(relation_terms[:6])
    return normalize_space(" ".join(_dedupe_terms(pieces)[:8]))


def check_query_quality(query: str | None) -> bool:
    if not query:
        return True

    terms = [t for t in query.split() if t.strip()]
    if len(terms) < 2:
        return True

    joined = query.lower().strip()
    bad_patterns = {
        "ability correct",
        "technology combination",
    }
    if joined in bad_patterns:
        return True

    return False