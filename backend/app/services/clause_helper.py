from app.services.model_helper import spacy

nlp = spacy.load("en_core_web_sm")

CLAUSE_CONNECTORS = {"and", "but", "while", "although", "though"}


def get_subject_text(span) -> str | None:
    for token in span:
        if token.dep_ in {"nsubj", "nsubjpass"}:
            subtree = list(token.subtree)
            subtree = sorted(subtree, key=lambda t: t.i)
            return " ".join(tok.text for tok in subtree)
    return None


def has_subject(span) -> bool:
    return any(token.dep_ in {"nsubj", "nsubjpass"} for token in span)


def has_finite_verb(span) -> bool:
    return any(token.pos_ in {"VERB", "AUX"} for token in span)


def clean_clause_text(text: str) -> str:
    text = text.strip(" ,;:-")
    if not text:
        return ""

    if not text.endswith((".", "!", "?")):
        text += "."

    return text


def split_sentence_into_clauses(sentence) -> list[str]:
    tokens = [token for token in sentence if not token.is_space]
    if not tokens:
        return []

    subject_text = get_subject_text(sentence)
    clauses = []
    start = 0

    for i, token in enumerate(tokens):
        if token.text.lower() not in CLAUSE_CONNECTORS:
            continue

        left = tokens[start:i]
        right = tokens[i + 1:]

        if not left or not right:
            continue

        left_span = sentence.doc[left[0].i : left[-1].i + 1]
        right_span = sentence.doc[right[0].i : right[-1].i + 1]

        # only split if the right side looks like its own predicate
        if not has_finite_verb(right_span):
            continue

        left_text = clean_clause_text(left_span.text)
        if left_text:
            clauses.append(left_text)

        right_text = right_span.text.strip()

        if right_text and not has_subject(right_span) and subject_text:
            right_text = f"{subject_text} {right_text}"

        right_text = clean_clause_text(right_text)
        if right_text:
            clauses.append(right_text)

        return clauses

    cleaned = clean_clause_text(sentence.text)
    return [cleaned] if cleaned else []


def split_extensive_claims(text: str) -> list[str]:
    doc = nlp(text)
    results = []

    for sentence in doc.sents:
        results.extend(split_sentence_into_clauses(sentence))

    return results